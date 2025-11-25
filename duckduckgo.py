import ssl
import os
import requests
import urllib3
from langchain_community.tools import DuckDuckGoSearchResults

# Comprehensive SSL certificate bypass for corporate environments
# Disable SSL verification globally
os.environ['PYTHONHTTPSVERIFY'] = '0'
os.environ['CURL_CA_BUNDLE'] = ''
os.environ['REQUESTS_CA_BUNDLE'] = ''

# Disable SSL warnings
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# Create unverified SSL context
ssl._create_default_https_context = ssl._create_unverified_context

# Monkey patch requests to disable SSL verification
original_request = requests.Session.request
def patched_request(self, method, url, **kwargs):
    kwargs.setdefault('verify', False)
    return original_request(self, method, url, **kwargs)
requests.Session.request = patched_request

try:
    search = DuckDuckGoSearchResults()
except Exception as e:
    print(f"Error initializing search tool: {e}")
    # Fallback: try with different parameters
    search = DuckDuckGoSearchResults(max_results=3)

print("DuckDuckGo Search Tool")
print("Type 'quit' or 'exit' to stop")
print("-" * 40)

while True:
    try:
        # Get user input
        query = input("\nEnter your search query: ").strip()
        
        # Check if user wants to quit
        if query.lower() in ['quit', 'exit', 'q']:
            print("Goodbye!")
            break
        
        # Skip empty queries
        if not query:
            print("Please enter a valid search query.")
            continue
        
        # Perform the search
        print(f"\nSearching for: {query}")
        print("-" * 40)
        
        try:
            result = search.invoke(query)
            print(result)
        except Exception as search_error:
            print(f"Primary search failed: {search_error}")
            print("Trying alternative approach...")
            
            # Alternative: Try with a simple web search using requests
            try:
                import json
                from duckduckgo_search import DDGS
                
                with DDGS() as ddgs:
                    results = list(ddgs.text(query, max_results=5))
                    if results:
                        print("Search Results:")
                        for i, result in enumerate(results, 1):
                            print(f"\n{i}. {result.get('title', 'No title')}")
                            print(f"   URL: {result.get('href', 'No URL')}")
                            print(f"   Snippet: {result.get('body', 'No description')}")
                    else:
                        print("No results found.")
            except ImportError:
                print("Alternative search library not available. Install with: pip install duckduckgo-search")
            except Exception as alt_error:
                print(f"Alternative search also failed: {alt_error}")
                print("This appears to be a network connectivity issue.")
        
        print("-" * 40)
        
    except KeyboardInterrupt:
        print("\n\nGoodbye!")
        break
    except Exception as e:
        print(f"Search failed with error: {e}")
        print("This might be due to network restrictions or SSL certificate issues.")
        print("Try a different query or check your network configuration.")