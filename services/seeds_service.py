from openpyxl import Workbook
from models.seeds_model import SeedsModel

class SeedsService:

    def __init__(self):
        self.model = SeedsModel()

    def generate_seeds_excel(self, slug):
        idtorneo = self.model.get_event_id(slug)
        seeds = self.model.get_seeds(idtorneo)

        wb = Workbook()
        ws = wb.active

        try:
            nombre_torneo = slug.split('/')[1]
        except:
            nombre_torneo = slug

        ws.title = "Seeds"
        ws.append(["Seed", "GamerTag"])

        for entry in seeds:
            ws.append([entry["seedNum"], entry["gamerTag"]])

        filename = f"Seeds - {nombre_torneo}.xlsx"
        wb.save(filename)
        return filename
