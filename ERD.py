from sqlalchemy_schemadisplay import create_schema_graph
from sqlalchemy import MetaData

def main():
    graph = create_schema_graph(metadata=MetaData('postgresql://postgres:postgres@172.17.0.2/sparkifydb'))
    graph.write_png('sparkifydb_erd.png')

if __name__ == "__main__":
    main()