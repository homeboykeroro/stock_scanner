import asyncio
import aiohttp
import time
import json

from utils.logger import Logger

logger = Logger()
loop = asyncio.new_event_loop()

async def fetch(session: aiohttp.ClientSession(), method: str, endpoint: str, payload: dict, semaphore):
    async with semaphore:
        try:
            if method == 'GET':
                logger.log_debug_msg(f"GET request with payload: {payload} send")
                async with session.get(endpoint, params=payload, ssl=False) as response:
                    json_response = await response.json()
                    logger.log_debug_msg(f"GET request with payload: {payload} response: {json_response}")
                    return json_response
            elif method == 'POST':
                async with session.post(endpoint, json=payload, ssl=False) as response:
                    json_response = await response.json()
                    logger.log_debug_msg(f"POST request with payload: {payload} response: {json_response}")
                    return await response.json()
            elif method == 'DELETE':
                async with session.delete(endpoint, json=payload, ssl=False) as response:
                    json_response = await response.json()
                    logger.log_debug_msg(f"POST request with payload: {payload} response: {json_response}")
                    return await response.json()
        except Exception as e:
            logger.log_error_msg(f'Error during {method} request to {endpoint}, payload: {payload}, Cause: {e}, Status code: {response.status}')
            return {'status': 'FAILED', 'errorMsg': str(e), 'payload': payload}

async def process_async_request(method: str, endpoint: str, payload_list: list, chunk_size: int, no_of_request_per_sec: int) -> dict:
    semaphore = asyncio.Semaphore(chunk_size)  # Limit to chunk_size concurrent requests
    result_dict = {'response_list': [], 'error_response_list': []}
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        
        all_chunk_start_time = time.time()
        
        for i, payload in enumerate(payload_list):
            task = asyncio.create_task(fetch(session, method, endpoint, payload, semaphore))
            tasks.append(task)
            
            # If we've hit the rate limit, sleep for a second
            if no_of_request_per_sec:
                if (i + 1) % chunk_size == 0:
                    logger.log_debug_msg(f'Wait {no_of_request_per_sec} to process next chunk')
                    await asyncio.sleep(no_of_request_per_sec)
        
        response_list = await asyncio.gather(*tasks, return_exceptions=True)
        logger.log_debug_msg(f'Completion of all async requests time: {time.time() - all_chunk_start_time} seconds')
        
        for response in response_list:
            if 'errorMsg' in response:
                result_dict['error_response_list'].append(response)
            else:
                result_dict['response_list'].append(response)
        
    return result_dict
        
def send_async_request(method: str, endpoint: str, payload_list: list, chunk_size: int, no_of_request_per_sec: float = None):
    #response_result = asyncio.run(process_async_request(method, endpoint, payload_list, chunk_size, no_of_request_per_sec))
    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
    
    response_result = loop.run_until_complete(process_async_request(method, endpoint, payload_list, chunk_size, no_of_request_per_sec))

    response_list = response_result['response_list']
    error_response_list = response_result['error_response_list']
    
    if len(error_response_list) > 0:
        raise Exception(f'Async requests not completed successfully, error response list: {json.dumps(error_response_list)}')
    
    return response_list