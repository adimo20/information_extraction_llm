from rapidfuzz import fuzz
import numpy as np

class DataAnnotator:
    def __init__(self, fulltext_dict, extracted_content_dict):
        self.extracted_content_dict = extracted_content_dict
        self.fulltext_dict = fulltext_dict
        self.threshold = 0.99
    
    def get_annotation_position(self, fulltext:str, extracted_text:str)-> tuple[int, int]:
        """Returns the string index of the extracted text
        Parameters:
            full_text
            extracted_text
        Returns:
            start, end 
        """
        index = fulltext.find(extracted_text)
        if index != -1:
            return index, index+len(extracted_text), "Exact_Match_Kontaktanzeige"
        return None
    
    def get_fuzzy_annotation_position(self, fulltext:str, extracted_text:str)-> tuple[int, int]:
        
        best_matches:list[str] = []
        best_ratios:list[float] = []
        lower_boundary,  upper_boundary = 0, len(extracted_text)-1
        len_fulltext:int = len(fulltext)
        while upper_boundary-1 <= len_fulltext-1:
            text_to_compare = fulltext[lower_boundary:upper_boundary]
            ratio = fuzz.ratio(text_to_compare, extracted_text)
            if ratio >= self.threshold:
                best_matches.append(text_to_compare)
                best_ratios.append(ratio)
            lower_boundary,  upper_boundary = lower_boundary+1,  upper_boundary+1
        
        if best_matches != []:
            best_match = best_matches[np.argmax(best_ratios)]
            index = fulltext.find(best_match)
            return index, index+len(best_match)-1, "Fuzzy_Match_Kontaktanzeige"
        else: 
            return None
    
    def make_entry(self, page_id, full_text):
        return {
            'id':page_id,
            'data':{
                'text':full_text
            },
            'annotations':[
                {
                    "result":[

                ]
            }]
        } 

    def add_annotations(self, start, end, extracted_content, id, label):
        return {
            "id": id,
            "from_name": "label", 
            "to_name": "text",
            "type": "labels",
            "value": {
                    "start": start,
                    "end": end,
                    "text": extracted_content,
                    "labels": [label] 
                    }
        }    
    
    def get_position(self, fulltext, extracted_text):
        exact_pos = self.get_annotation_position(fulltext, extracted_text)
        if exact_pos is not None:
            return exact_pos        
        fuzzy_pos = self.get_fuzzy_annotation_position(fulltext, extracted_text)
        if fuzzy_pos is not None:
            return fuzzy_pos
        return None, None, None
        
        

    def annotate_data(self):
        keys = [x for x in self.extracted_content_dict.keys()]
        result_list = []
        for k in keys:
            if k not in self.fulltext_dict.keys():continue
            current_fulltext = self.fulltext_dict[k]
            entry = self.make_entry(k, current_fulltext)
            for i, text in enumerate(self.extracted_content_dict[k]):
                lower, upper, label = self.get_position(current_fulltext, text)
                #add_annotations(self, start, end, extracted_content, id, label):
                if lower is None: continue # das hier müsste man ändern!
                curr_id = k + "_" + str(i)
                entry["annotations"][0]["result"].append(
                    self.add_annotations(
                        start=lower,
                        end=upper,
                        extracted_content=text,
                        id=curr_id,
                        label=label)
                )
            result_list.append(entry)
        return result_list
        


            
                

    


