"""Crea la base (esquema + 3 registros DEMO). Idempotente: no duplica al repetirse."""
import oes_db


def main() -> None:
    ruta = oes_db.ruta_db()
    con = oes_db.conectar(ruta)
    try:
        oes_db.crear_esquema(con)
        oes_db.insertar_demo(con)
        total = con.execute("SELECT COUNT(*) FROM noticias").fetchone()[0]
    finally:
        con.close()
    print(f"Base creada: {ruta}")
    print(f"Total de filas: {total}")


if __name__ == "__main__":
    main()
