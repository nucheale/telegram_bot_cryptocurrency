import logging
from g4f.client import ClientFactory


client = ClientFactory.create_client("azure")

async def get_response(prompt):
    response = None
    try:
        response_object = client.chat.completions.create(
            model="model-router3",
            messages=[{"role": "user", "content": prompt}],
        )
        response = response_object.choices[0].message.content
    except Exception as e:
        logging.error(e)
        response = "Запрос не выполнен. Попробуйте еще раз."
    finally:
        return response


async def ai_all_models(prompt):
    response = None
    try:
        response = await get_response(prompt)
        if not response == "Запрос не выполнен. Попробуйте еще раз.":
            return response
    except Exception as e:
        logging.error(e)
        response = "Запрос не выполнен. Попробуйте еще раз."
    finally:
        return response