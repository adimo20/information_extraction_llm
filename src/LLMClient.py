import pandas as pd
import google.generativeai as genai
import os
import json

# Definieren einer Klasse LLMWorker

# - Diese Klasse versucht, das was in `Scripts/information_extractor_lib` als `Information_Extractor` definiert wurde zu vereinfachen, 
# da hier anstatt "relativ umständlich" mit Dataframe zu arbeiten direkt mit dicionarys gearbeitet wird, welches iterativ ergänzt wird und
# dann am ende zu einem Dataframe exploded wird.

# - Mittels dieser Klasse können wir durch Vererbung des gesamten Workflow in einer zweiten Klasse automatiseren. D.h. wir müssen nicht
#  mehr drei verschiedene Objekte intialisieren (ist aber nicht zwingend notwendig - LLMWorker kann auch allein für einen einzigen Task
#  verwendet werden). 

class LLMWorker:
    def __init__(self, configs:dict, input_id:list[str], text:list[str]):
        self.config:dict = configs
        self.initialized_model:bool = False
        self.input_id:list[str] = input_id if isinstance(input_id, list) else [input_id]
        self.text:list[str] = text if isinstance(text, list) else [text]
        self.model = None
        self.output = {"results": { } }
        self.prompt_key = 'PROMPT'
        
    def set_config(self) -> None:
        """Setzen des API Keys, aus den im config dict gespeicherten Daten"""
        API_KEY = self.config["API_KEY"]
        genai.configure(api_key=API_KEY)

    def load_model(self) -> None:
        """Laden des Models und setzen der Modelkonfigurationen. Generation Config sollte im config_file gespeichert sein"""
        self.model = genai.GenerativeModel(
            model_name=self.config["model_name"],
            generation_config=self.config["generation_config"])
        self.initialized_model = True

    def create_model_input(self,page_id:str, input_text:str) -> str:
        """Funktion die den prompt erstellt, der später an die Model API gesendet wird
        Parameters:
        page_id - id des inputs
        input_text - Text der als Input für das Model verwendet wird

        Returns:
        string that combines the input text and input prompt
        
        """
        
        model_input = {page_id:input_text}
        input_combined = f"{self.config[self.prompt_key]}\n{model_input}"
        return input_combined
    
    
    def extract_single_page(self, page_id:str, input_text:str) -> dict:
        """Funktion die die API anspricht und die einen strukturierten Output als response erhält
        Parameters:
        page_id - id des inputs
        input_text - Text der als Input für das Model verwendet wird

        Returns:
        model response
        """
        try:
            input_combined = self.create_model_input(page_id=page_id, input_text=input_text)
            
        except Exception as e:
            print(f"Error while generating the model input: {e}")
            return {"content":f"Error while generating the model input: {e}"}
        
        try:
            response = self.model.generate_content([input_combined])
        except Exception as e:
            print(f"Error while receiving the response: {e} ")
            return {"content":f"Error while receiving the response: {e} "}
        
        try:
            res_parsed = json.loads(str(response.text))

            return res_parsed
        except Exception as e: 
            print(f"Error while parsing the response - Exeption {e}")
            return {"content":f"Error while parsing the response - Exeption {e}"}
        
    def extract_content(self):
        if self.initialized_model is False:
            self.set_config()
            self.load_model()
        current_idx = 0
        for p_, t_ in zip(self.input_id, self.text):
            print(p_)
            result = self.extract_single_page(p_, t_)
            #Wenn mehr als eine Id vorhanden, dann wird pro id jeweils ein index ergänzt für den eintrag im dict, sonst überschreiebn wir den eintrag wieder
            if str(p_) in self.output["results"].keys():
                self.output["results"].update({str(p_+"anz_" + str(current_idx)):result["content"]})
                current_idx += 1
            else:
                self.output["results"].update({str(p_):result["content"]})
                current_idx = 0
            
        return self.output
    

def output_to_df(output:dict):
    extracted_list = []
    ids = []
    for k in output["results"].keys():
        extracted_list.append(output["results"][k])
        ids.append(k)
    df = pd.DataFrame(data={"ids":ids, "content":extracted_list})
    df = df.explode('content').reset_index(drop=True)
    return df


def dict_to_df(result:dict)-> pd.DataFrame:
    df = pd.DataFrame.from_dict(result)
    df["id"] = df.index
    df = df.reset_index(drop=True)
    df.columns = ["text", id]
    df = df.explode("text").reset_index(drop=True)
    return df



