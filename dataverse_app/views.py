from django.http import JsonResponse
from rest_framework.views import APIView
from django.views import View
import requests
import logging
import time

# Set up logging
logger = logging.getLogger(__name__)

class DataverseAllView(APIView):
    def get(self, request):
        base_url = "https://dataverse.harvard.edu"
        per_page = 100
        max_loops = 40
        all_global_ids = []

        start_time = time.time()  # Record the start time

        for loop in range(max_loops):
            # Build the API URL for the search with the appropriate start parameter for pagination
            start = loop * per_page
            api_url = f"{base_url}/api/search?q=*&type=dataset&per_page={per_page}&start={start}"

            # Make the request to the Dataverse API
            response = requests.get(api_url)

            if response.status_code == 200:
                search_results = response.json()["data"]["items"]
                if not search_results:
                    break  # Break the loop if no more results are returned
                for result in search_results:
                    global_id = result.get("global_id")
                    all_global_ids.append(global_id)
            else:
                return JsonResponse({"error": f"Error retrieving global IDs. Status code: {response.status_code}"}, status=response.status_code)

        end_time = time.time()  # Record the end time
        duration = end_time - start_time  # Calculate the duration

        print(f"Gathered {len(all_global_ids)} global IDs in {duration:.2f} seconds")  # Print the duration

        return JsonResponse(all_global_ids, safe=False)

class DataverseSearchView(View):
    def get(self, request):
        query = request.GET.get('query', '')  # Get the search query from the request
        base_url = "https://dataverse.harvard.edu"
        per_page = 30
        start = 0
        all_results = []
        loop_count = 0
        max_loops = 5  # Maximum number of loops

        # Loop to fetch all search results in batches
        while loop_count < max_loops:
            # Build the API URL for the search
            api_url = f"{base_url}/api/search?q={query}&type=dataset&per_page={per_page}&start={start}"
            
            # Make the request to the Dataverse API
            response = requests.get(api_url)
            
            if response.status_code == 200:
                search_results = response.json()["data"]["items"]
                if not search_results:  # Break the loop if no more results
                    break
                all_results.extend([{"title": result["name"], "global_id": result["global_id"]} for result in search_results])
                start += per_page  # Update the start parameter for the next batch
                loop_count += 1  # Increment the loop count
                print(f"Loop {loop_count}: Retrieved {len(search_results)} items")
            else:
                print(f"Error retrieving search results. Status code: {response.status_code}. Returning items retrieved so far.")
                break  # Exit the loop if there's an error

        return JsonResponse(all_results, safe=False)  # Return the results gathered so far
        
# class DataverseView(APIView):
#     def get(self, request):
#         base_url = "https://dataverse.harvard.edu"
#         dataset_id = "doi:10.7910/DVN/DHRV46"
#         # dataset_id = "doi:10.7910/DVN/NMPWH2"

#         api_url = f"{base_url}/api/datasets/:persistentId?persistentId={dataset_id}"
#         response = requests.get(api_url)
        
#         if response.status_code == 200:
#             dataset_metadata = response.json()["data"]
#             latest_version = dataset_metadata.get("latestVersion", {})
#             citation_metadata = latest_version.get("metadataBlocks", {}).get("citation", {})
#             persistent_url = dataset_metadata.get("persistentUrl")

#             # Extract the title
#             title_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "title"), None)
#             title = title_field["value"] if title_field else None
            
#             # Extract the description
#             description_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "dsDescription"), None)
#             description = description_field.get("value")[0].get("dsDescriptionValue", {}).get("value") if description_field else None
            
#             # Extract the subject
#             subject_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "subject"), None)
#             subjects = subject_field["value"] if subject_field else []

#             # Extract the keywords
#             keyword_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "keyword"), None)
#             keywords = [item["keywordValue"]["value"] for item in keyword_field["value"]] if keyword_field else []

#             # Extract the publications
#             publication_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "publication"), None)
#             publications = [item["publicationCitation"]["value"] for item in publication_field["value"]] if publication_field else []

#             dataset_info = {
#                 "title": title,
#                 "description": description,

#                 "subject": subjects,
#                 "keywords": keywords,
#                 "publications": publications,
#                 "releaseTime": latest_version.get("releaseTime"),
#                 "lastUpdateTime": latest_version.get("lastUpdateTime"),
#                 "persistentUrl": persistent_url,
#                 "datasetPersistentId": dataset_id,
#                 "datasetId": dataset_metadata.get("id")
#             }
#             return JsonResponse(dataset_info)
#         else:
#             return JsonResponse({"error": f"Error retrieving dataset metadata. Status code: {response.status_code}"}, status=response.status_code)


class DataverseView(APIView):
    def get(self, request):
        base_url = "https://dataverse.harvard.edu"
        # dataset_ids = request.GET.getlist('dataset_id')  # Get the array of dataset_ids from the request
        dataset_ids = ["doi:10.7910/DVN/DHRV46","doi:10.7910/DVN/NMPWH2"]
        all_datasets_info = []

        for dataset_id in dataset_ids:
            api_url = f"{base_url}/api/datasets/:persistentId?persistentId={dataset_id}"
            response = requests.get(api_url)
            
            if response.status_code == 200:
                dataset_metadata = response.json()["data"]
                latest_version = dataset_metadata.get("latestVersion", {})
                citation_metadata = latest_version.get("metadataBlocks", {}).get("citation", {})
                persistent_url = dataset_metadata.get("persistentUrl")

                # Extract the title
                title_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "title"), None)
                title = title_field["value"] if title_field else None
                
                # Extract the description
                description_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "dsDescription"), None)
                description = description_field.get("value")[0].get("dsDescriptionValue", {}).get("value") if description_field else None
                
                # Extract the subject
                subject_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "subject"), None)
                subjects = subject_field["value"] if subject_field else []

                # Extract the keywords
                keyword_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "keyword"), None)
                keywords = [item["keywordValue"]["value"] for item in keyword_field["value"]] if keyword_field else []

                # Extract the publications
                publication_field = next((field for field in citation_metadata.get("fields", []) if field["typeName"] == "publication"), None)
                publications = [item["publicationCitation"]["value"] for item in publication_field["value"]] if publication_field else []

                dataset_info = {
                    "title": title,
                    "description": description,
                    "subject": subjects,
                    "keywords": keywords,
                    "publications": publications,
                    "releaseTime": latest_version.get("releaseTime"),
                    "lastUpdateTime": latest_version.get("lastUpdateTime"),
                    "persistentUrl": persistent_url,
                    "datasetPersistentId": dataset_id,
                    "datasetId": dataset_metadata.get("id")
                }

                all_datasets_info.append(dataset_info)
            else:
                all_datasets_info.append({"error": f"Error retrieving metadata for dataset {dataset_id}. Status code: {response.status_code}"})

        return JsonResponse(all_datasets_info, safe=False)
        # dataset_id = "doi:10.7910/DVN/DHRV46"
        # dataset_id = "doi:10.7910/DVN/NMPWH2"


            # description = dataset_metadata.get("description")
            # subject = dataset_metadata.get("subjects")
            # keywords = dataset_metadata.get("keywords")
            # related_publications = dataset_metadata.get("publications")
            # license = dataset_metadata.get("license")
# class DataverseView(APIView):
#     def get(self, request):
#         base_url = "https://demo.dataverse.org/api"
#         dataverse_id = "root"
#         page_size = 100
#         start = 0
        
#         datasets = []
        
#         while True:
#             api_url = f"{base_url}/dataverses/{dataverse_id}/contents?type=dataset&per_page={page_size}&start={start}"
#             response = requests.get(api_url)
            
#             if response.status_code == 200:
#                 data = response.json()
#                 items = data['data']
#                 datasets.extend(items)
                
#                 if len(items) < page_size:
#                     break
                
#                 start += page_size
#             else:
#                 return JsonResponse({"error": f"Error retrieving data: {response.status_code}"}, status=response.status_code)
        
#         return JsonResponse({"datasets": datasets}, safe=False)