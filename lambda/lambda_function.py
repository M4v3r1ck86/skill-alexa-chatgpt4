import logging

import openai
from ask_sdk_core.dispatch_components import (AbstractExceptionHandler,
                                              AbstractRequestHandler)
from ask_sdk_core.handler_input import HandlerInput
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_model import Response

# Configure your OpenAI API key
openai.api_key = "substitua-pela-sua-chave-da-openai"

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

messages = [{"role": "system", "content": "Você é uma assistente muito útil. Por favor, responda de forma clara e concisa em Português do Brasil."}]

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        speak_output = "Bem vindo ao Chat 'Gepetê Quatro' da 'Open ei ai'! Qual a sua pergunta?"
        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class GptQueryIntentHandler(AbstractRequestHandler):
    """Handler for Gpt Query Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("GptQueryIntent")(handler_input)

    def handle(self, handler_input):
        query = handler_input.request_envelope.request.intent.slots["query"].value
        response = generate_gpt_response(query)

        return (
            handler_input.response_builder
                .speak(response)
                .ask("Alguma outra pergunta?")
                .response
        )

class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Desculpe, não consegui obter uma resposta para esta pergunta. Tente perguntar de outra forma."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Saindo do modo Chat Gepetê."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )

def generate_gpt_response(query):
    try:
        messages.append(
            {"role": "user", "content": query},
        )
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",  # Use o modelo GPT-3.5 Turbo
            messages=messages,
            max_tokens=1000,
            n=1,
            stop=None,
            temperature=0.5
        )
        reply = response['choices'][0]['message']['content'].strip()
        messages.append({"role": "assistant", "content": reply})
        return reply
    except Exception as e:
        return f"Erro ao gerar resposta: {str(e)}"

sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(GptQueryIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())
