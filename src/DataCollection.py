import pandas as pd
from ddbapi import zp_pages

default_places = [
    "Stuttgart", "Köln", "Hamburg", "Bonn", "Bad Godesberg", "Kleve (Kreis Kleve)", "Jülich", "Dortmund",
    "Siegburg", "Euskirchen", "Halle (Saale)", "Münster (Westf)", "Berlin", "Duisburg", "Bielefeld",
    "Stuttgart-Untertürkheim", "Untertürkheim", "Feuerbach (Stuttgart)", "Stuttgart-Feuerbach", "Stuttgart-Zuffenhausen",
    "Zuffenhausen", "Botnang", "Degerloch", "Münster (Stuttgart)", "Obertürkheim", "Stuttgart-Botnang",
    "Stuttgart-Degerloch", "Stuttgart-Münster", "Stuttgart-Obertürkheim", "Aachen", "Ruhrort", "Bonn-Bad Godesberg",
    "Karlsruhe", "Solingen", "Moers", "Meiderich", "Regierungsbezirk Aachen", "Düren", "Mannheim", "Beckum",
    "Mülheim an der Ruhr", "Gütersloh", "München-Gladbach", "Warendorf", "Ahlen (Kreis Warendorf)", "Dinslaken",
    "Mönchengladbach", "Gladbach-Rheydt", "Ohligs", "Oelde", "Wiedenbrück", "Dresden", "Iserlohn", "Hamborn",
    "Oberhausen (Rheinland)", "Wesel", "Düsseldorf", "Biberach an der Riß", "Merseburg", "Kreis Solingen",
    "Gräfrath", "Duisburg-Hamborn", "Bad Buchau", "Hagen", "Hamburg-Harburg", "Harburg (Elbe)",
    "Harburg-Wilhelmsburg", "Arnsberg", "Haan", "Riedlingen", "Wülfrath", "Witten", "Krefeld", "Velbert",
    "Velbert-Langenberg", "Mettmann", "Hamm (Westf)", "Soest", "Werl", "Hannover", "Geldern", "Bergheim (Erft)",
    "Bergedorf", "Castrop-Rauxel", "Geesthacht", "Hamburg-Bergedorf", "Hamburg-Lohbrügge", "Stormarn", "Leipzig",
    "Bensberg", "Bergisch Gladbach", "Bergisch Gladbach-Bensberg", "Schwarzenberg/Erzgeb.", "Dorsten",
    "Ochsenhausen", "Heiligenhaus", "Neviges", "Landkreis Kempen-Krefeld", "New York, NY", "Heidelberg"
]
class DataCollector:
    def __init__(self, places:list[str]=None, write_output:bool=False, output_path:str=None, query:list[str]=None):
        self.places:list[str] = default_places if places is None else places
        self.write_output = write_output
        self.output_path = output_path
        self.query = query
        self.retrieved_data = None

    def save_data(self)->None:
        """Write a csv output file to the place set in output path"""
        if self.write_output:
            self.retrieved_data.to_csv(self.output_path)
        return
        
    def get_data_from_query(self) -> None:

        """
        Loads data from ddbapi and saves it as a pandas df object into self.retrieved_data
        """

        df_list = []
        for q in self.query:
            for place in self.places:
                df = zp_pages(
                    publication_date='[1850-01-01T12:00:00Z TO 1980-12-31T12:00:00Z]', 
                    place_of_distribution=place, 
                    plainpagefulltext=q
                    )
                if df is not None and len(df) > 0:
                    df["query"] = q
                    df_list.append(df)
        

        if len(df_list) > 1:
            self.retrieved_data = pd.concat(df_list)
            self.retrieved_data.drop_duplicates(subset="plainpagefulltext")
            self.save_data()
        else:
            self.retrieved_data = df_list[0]
            self.retrieved_data.drop_duplicates(subset="plainpagefulltext")
            self.save_data()
        return self.retrieved_data
    
    def create_random_sample(self):
        return self.retrieved_data.sample(100).reset_index(drop=True)

