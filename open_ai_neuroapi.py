from config_data import config
import openai
import logging

openai.api_key = config.NEUROAPI_KEY.get_secret_value()
openai.api_base = "https://neuroapi.host/v1"


# def chatgpt_main(prompt):
#     chat_completion = openai.ChatCompletion.create(
#         model="gpt-3.5-turbo",
#         messages=[{"role": "user", "content": prompt}],
#         stream=True,
#     )
#
#     if isinstance(chat_completion, dict):
#         # not stream
#         # print("not stream")
#         print(chat_completion.choices[0].message.content)
#         # chatgpt_answer = chat_completion.choices[0].message.content
#     else:
#         # stream
#         answer = ""
#         for token in chat_completion:
#             content = token["choices"][0]["delta"].get("content")
#             if content is not None:
#                 # print("stream")
#                 print(content, end="", flush=True)
#                 answer += content
#     print(answer)
#     return answer


async def chatgpt_main(prompt) -> dict:
    try:
        chat_completion = await openai.ChatCompletion.acreate(
            # model="gpt-3.5-turbo",
            model="gpt-3.5-turbo-16k",
            messages=[
                {"role": "user", "content": prompt}
            ]
        )
        # print(chat_completion['choices'][0]['message']['content'])
        return chat_completion['choices'][0]['message']['content']
    except Exception as e:
        logging.error(e)

#
# if __name__ == "__main__":
#     chatgpt_main()
