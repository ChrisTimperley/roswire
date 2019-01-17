__all__ = ['Container']

from uuid import UUID

from bugzoo import BugZoo as BugZooDaemon
from bugzoo import Container as BugZooContainer


class Container(object):
    def __init__(self,
                 daemon_bugzoo: BugZooDaemon,
                 container_bugzoo: BugZooContainer,
                 uuid: UUID
                 ) -> None:
        self.__daemon_bugzoo = daemon_bugzoo
        self.__container_bugzoo = container_bugzoo
        self.__uuid = uuid
