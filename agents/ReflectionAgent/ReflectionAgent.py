from groq import Groq
import os
from ..utils.completion import InitializeChatHistory, build_prompt_structure, update_chat_history
from ..utils.logging import fancy_step_tracker
from colorama import Fore

class ReflectionAgent:

    def __init__(self, model: str = "llama3-70b-8192"): #"llama3-8b-8192"
        self.client = Groq(api_key=os.environ.get("groq_api_key"))
        self.model = model
        self.generation_system_prompt = '''
        Your task is to Generate the best content possible for the user's request.
        If the user provides critique, respond with a revised version of your previous attempt.
        You must always output the revised content.
        '''
        self.reflection_system_prompt = '''
        You are tasked with generating critique and recommendations to the user's generated content.
        If the user content has something wrong or something to be improved, output a list of recommendations
        and critiques. If the user content is ok and there's nothing to change, output this: <STOP>
        '''

    def _model(self, history: list, verbose: int = 0, log_title: str = "COMPLETION", log_color: str = ""):
        chat_completion = self.client.chat.completions.create(
            messages=history,
            model=self.model,
        )

        if verbose > 0:
            print(log_color, f"\n\n{log_title}\n\n", chat_completion)

        return str(chat_completion.choices[0].message.content)

    def generate(self, generation_history: list, verbose: int = 0):

        return self._model(generation_history, verbose=verbose, log_title="GENERATION", log_color=Fore.BLUE)
    
    def reflect(self, reflection_history: list, verbose: int = 0):

        return self._model(reflection_history, verbose=verbose, log_title="REFLECTION", log_color=Fore.GREEN)
    
    def invoke(self, message: str, n_iterations: int, verbose: int = 0):

        generation_history = InitializeChatHistory([
            build_prompt_structure(prompt=self.generation_system_prompt, role="system"),
            build_prompt_structure(prompt=message, role="user")
        ], total_length=2)

        reflection_history = InitializeChatHistory([
            build_prompt_structure(self.reflection_system_prompt, role="system"),

        ], total_length=2)

        for step in range(n_iterations):
            if verbose > 0:
                fancy_step_tracker(step, n_iterations)

            generation = self.generate(generation_history, verbose=verbose)
            generation_history.append(build_prompt_structure(prompt=generation, role="assistant"))
            reflection_history.append(build_prompt_structure(generation, role="user"))

            reflection = self.reflect(reflection_history, verbose=verbose)

            if "<STOP>" in reflection:
                print(
                    Fore.RED,
                    "\n\nStop Sequence found. Stopping the reflection loop ... \n\n",
                )
                break

            generation_history.append(build_prompt_structure(prompt=reflection, role="user"))
            reflection_history.append(build_prompt_structure(prompt=reflection, role="assistant"))

        return generation