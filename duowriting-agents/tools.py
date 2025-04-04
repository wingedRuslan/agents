import os
import json
import requests
from typing import Dict, Annotated


def _process_search_results(raw_results: Dict, query: str) -> Dict:
    """
    Process raw search results and extract the most relevant information.
    
    Args:
        raw_results: The raw JSON response from the search API
        query: The original search query
        
    Returns:
        A dictionary containing organized search results with only the most relevant information
    """
    organized_results = {
        "query": query,
        "results": []
    }
    
    # Extract Knowledge Graph information if available
    if "knowledgeGraph" in raw_results:
        kg = raw_results["knowledgeGraph"]
        knowledge_graph = {
            "title": kg.get("title", ""),
            "description": kg.get("description", ""),
            "attributes": kg.get("attributes", {})
        }
        organized_results["knowledge_graph"] = knowledge_graph
    
    # Extract organic search results
    if "organic" in raw_results:
        for result in raw_results["organic"][:5]:  # Limit to top 5 results
            organized_results["results"].append({
                "title": result.get("title", ""),
                "snippet": result.get("snippet", ""),
                "link": result.get("link", "")
            })
    
    # Extract top stories if available
    if "topStories" in raw_results and raw_results["topStories"]:
        organized_results["top_stories"] = []
        for story in raw_results["topStories"][:3]:  # Limit to top 3 stories
            organized_results["top_stories"].append({
                "title": story.get("title", ""),
                "source": story.get("source", ""),
                "date": story.get("date", ""),
                "link": story.get("link", "")
            })
    
    # Extract people also ask questions
    if "peopleAlsoAsk" in raw_results:
        organized_results["related_questions"] = []
        for question in raw_results["peopleAlsoAsk"]:
            organized_results["related_questions"].append({
                "question": question.get("question", ""),
                "snippet": question.get("snippet", "")
            })
    
    return organized_results


def google_search(query: Annotated[str, "The search query to look up information"]) -> Dict:
    """
    Perform a Google search using the Serper API.
    
    Args:
        query: The search query string
        
    Returns:
        A dictionary containing organized search results with only the most relevant information
    """
    url = "https://google.serper.dev/search"
    
    payload = json.dumps({
        "q": query
    })
    
    headers = {
        'X-API-KEY': os.getenv('SERPER_API_KEY'),
        'Content-Type': 'application/json'
    }
    
    try:
        response = requests.request("POST", url, headers=headers, data=payload)
        response.raise_for_status()

        # Parse and extract only the relevant information
        raw_results = response.json()
        return _process_search_results(raw_results, query)
    
    except requests.exceptions.RequestException as e:
        return {"error": str(e), "message": "Failed to perform search"}

