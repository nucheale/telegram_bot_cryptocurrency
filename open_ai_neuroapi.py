from config_data import config
import openai
import logging

openai.api_key = config.NEUROAPI_KEY.get_secret_value()
openai.api_base = "https://neuroapi.host/v1"
models = ["gpt-3.5-turbo", "gpt-3.5-turbo-0613", "gpt-3.5-turbo-1106", "gpt-3.5-turbo-16k", "gpt-3.5-turbo-16k-0613"]


async def chatgpt_main(model, prompt) -> dict:
    response = None
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            model=model,
            messages=[{"role": "user", "content": prompt}]
        )
        # print(chat_completion['choices'][0]['message']['content'])
        response = chat_completion['choices'][0]['message']['content']
    except Exception as e:
        logging.error(e)
        response = "Запрос не выполнен. Попробуйте еще раз."
    finally:
        return response


async def chatgpt_all_models(prompt):
    response = None
    try:
        for model in models:
            response = await chatgpt_main(model, prompt)
            if not response == "Запрос не выполнен. Попробуйте еще раз.":
                return response
    except Exception as e:
        logging.error(e)
        response = "Запрос не выполнен. Попробуйте еще раз."
    finally:
        return response
