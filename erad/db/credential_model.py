""" Module for storing pydantic model for neo4j credential. """

from pydantic import BaseModel, validator

from erad.exceptions import DatabaseMissingInfo


class Neo4jConnectionModel(BaseModel):
    neo4j_url: str
    neo4j_username: str
    neo4j_password: str

    @validator("neo4j_url", "neo4j_username", "neo4j_password")
    def check_string(cls, value):
        if not all(value):
            raise DatabaseMissingInfo(
                "Credential and/or connection URL missing \
                to connect to Neo4J database!"
            )
        return value
