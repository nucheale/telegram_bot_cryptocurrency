# from config_data import config
import g4f
import asyncio
import logging
# from g4f.client import Client


g4f.debug.version_check = False

_providers = [
    g4f.Provider.FlowGpt,
    g4f.Provider.AItianhuSpace,
    g4f.Provider.ChatForAi,
    g4f.Provider.Chatgpt4Online,
    g4f.Provider.ChatgptNext,
    g4f.Provider.ChatgptX,
    g4f.Provider.FreeGpt,
    g4f.Provider.GptTalkRu,
    g4f.Provider.Koala,
    g4f.Provider.MyShell,
    g4f.Provider.PerplexityAi,
    g4f.Provider.TalkAi,
    g4f.Provider.Vercel
]


async def run_provider(provider: g4f.Provider.BaseProvider, prompt):
    response = None
    try:
        response = await g4f.ChatCompletion.create_async(
            model=g4f.models.default,
            messages=[{"role": "user", "content": prompt}],
            provider=provider,
        )
        # print(f"{provider.__name__}:", response)
    except Exception as e:
        # print(f"err: {provider.__name__}:", e)
        logging.error(e)
        response = "Запрос не выполнен. Попробуйте еще раз."
    finally:
        return response


async def chatgpt_all_models(prompt):
    response = None
    try:
        counter = 0
        for provider in _providers:
            calls = [run_provider(provider, prompt)]
            # await asyncio.gather(*calls)
            response = await asyncio.gather(*calls)
            if not response[counter] == "Запрос не выполнен. Попробуйте еще раз.":
                return response
            counter += 1
    except Exception as e:
        logging.error(e)
        response = "Запрос не выполнен. Попробуйте еще раз."
    finally:
        print(response[0])
        return response[0]


# asyncio.run(chatgpt_all_models())
