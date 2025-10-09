from utils.reportes.reporte_word import ReporteDocumento

class ReporteManager:
    _reportes = {}

    @classmethod
    def obtener(cls, categoria: str) -> ReporteDocumento:

        if categoria not in cls._reportes:
            cls._reportes[categoria] = ReporteDocumento(categoria)
        return cls._reportes[categoria]

    @classmethod
    def guardar_todos(cls) -> None:
        for categoria, reporte in cls._reportes.items():
            print(f"Guardando reporte: {categoria}")
            ruta = reporte.guardar()
            print(f"Reporte guardado en: {ruta}")
            #print(f"Guardando reporte {categoria}")