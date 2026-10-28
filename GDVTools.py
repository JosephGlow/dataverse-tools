"""
Glow's Dataverse Tools
\n Personal toolkit for interacting with Microsoft Dataverse, Dynamics and Power Platform with Python using the new Dataverse SDK for Python.
\n Dependencies: https://learn.microsoft.com/en-us/power-apps/developer/data-platform/sdk-python/overview
"""
from azure.identity import InteractiveBrowserCredential
from azure.core.credentials import TokenCredential

from PowerPlatform.Dataverse.client import DataverseClient
from PowerPlatform.Dataverse.core.config import DataverseConfig

def login(base_url:str,credential:TokenCredential=None):
    """Log in to DataverseClient using Azure PKCE or manual browser login, log out after.
          
    Required
    ________ 
    `base_url`: Environment URL; *"`https://glowdata.crm11.dynamics.com`"*  
      
    Optional
    ________  
    `credential`: Proof Key for Code Exchange; `TokenCredential`_; *None* prompts manual login using Azure's `InteractiveBrowserCredential()`_.  

    .. _InteractiveBrowserCredential(): https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python
    .. _TokenCredential: https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.credentials.tokencredential?view=azure-python
    """
    
    if credential is None:
        try:
            credential = InteractiveBrowserCredential()
        except:
            raise    
    
    try:
        return DataverseClient(base_url, credential)
    except:
        raise

def rowcount(table:str,tuid:str,base_url:str,statecode:int=None,credential=None,print_progress:bool=None):
    """Read-only count of total rows/records in a Dataverse table.
    
    Required
    ________ 
    `table`: Logical name; *"contact"*  
    `uid`: Table's unique identifier/GUID column; *"contactid"*  
    `base_url`: Environment URL; *"`https://glowdata.crm11.dynamics.com`"*  
      
    Optional
    ________  
    `credential`: Proof Key for Code Exchange; `TokenCredential`_; *None* prompts manual login using Azure's `InteractiveBrowserCredential()`_.  
    `statecode`: Filter rows counted by StateCode choice integer Value; 0/1/...; *None* counts rows regardless of status.  
    `print_progress`: bool (True = print batch processing information and final count, False/None = pass)
    
    .. _InteractiveBrowserCredential(): https://learn.microsoft.com/en-us/python/api/azure-identity/azure.identity.interactivebrowsercredential?view=azure-python
    .. _TokenCredential: https://learn.microsoft.com/en-us/python/api/azure-core/azure.core.credentials.tokencredential?view=azure-python
    """
    
    if statecode is None:
        batch_filter = ""
        last_filter = ""
    else:
        batch_filter = f"WHERE statecode = {statecode}"
        last_filter = f"AND statecode = {statecode}"

    if print_progress == True:
        p_batch = print(f"Processed batch: {batch_count}, running total: {total_count}")
        p_final = print(f"\n Final total contacts: {total_count}")
    else:
        p_batch = None
        p_final = None

    client = login(base_url,credential)

    batch_size = 5000
    last_id = None
    total_count = 0
    
    while True:
        if last_id:
            query = f"""
                SELECT TOP {batch_size} {tuid}
                FROM {table} WHERE {tuid} > '{last_id}'{last_filter}
                ORDER BY {tuid}
            """
        else:
            query = f"""
                SELECT TOP {batch_size} {tuid}
                FROM {table} {batch_filter}
                ORDER BY {tuid}
            """

        results = client.query.sql(query)
        rows = list(results)
        batch_count = len(rows)

        if batch_count == 0:
            break

        total_count += batch_count

        # prep for next batch
        last_id = rows[-1][tuid]
        p_batch

    p_final
    return total_count
