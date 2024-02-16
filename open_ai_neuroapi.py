from config_data import config
import openai
import logging

openai.api_key = config.NEUROAPI_KEY.get_secret_value()
openai.api_base = "https://neuroapi.host/v1"


async def chatgpt_main(prompt) -> dict:
    response = None
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            # model="gpt-3.5-turbo",
            # model="gpt-3.5-turbo-16k",
            model="gpt-3.5-turbo-1106",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # print(chat_completion['choices'][0]['message']['content'])
        response = chat_completion['choices'][0]['message']['content']
    except Exception as e:
        logging.error(e)
        response = "Запрос не выполненнннннннннннннннн! Попробуй еще раз..."
    finally:
        return response


async def chatgpt_any_request(prompt) -> dict:
    response = None
    # model = 'gpt-3.5-turbo'
    # model = 'gpt-3.5-turbo-16k'
    model = 'gpt-3.5-turbo-1106'
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            # model="gpt-3.5-turbo",
            # model="gpt-3.5-turbo-16k",
            # model="gpt-3.5-turbo-1106",
            model=model,
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # print(chat_completion['choices'][0]['message']['content'])
        response = chat_completion['choices'][0]['message']['content']
    except Exception as e:
        logging.error(e)
        response = "Превышено время ожидания, запрос не выполнен"
    finally:
        return response
