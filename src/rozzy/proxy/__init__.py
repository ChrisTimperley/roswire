__all__ = [
    'ShellProxy',
    'ServiceManagerProxy',
    'ParameterServerProxy',
    'NodeManagerProxy',
    'NodeProxy',
    'ROSProxy',
    'BagRecorderProxy',
    'FileProxy'
]

from typing import (Tuple, Dict, Optional, Iterator, Any, List, Union,
                    Collection)
import os
import xmlrpc.client
import logging
import time

from .shell import ShellProxy
from .file import FileProxy
from .parameters import ParameterServerProxy
from .bag import BagRecorderProxy
from .node import NodeProxy, NodeManagerProxy
from .service import ServiceManagerProxy
from ..exceptions import RozzyException

logger = logging.getLogger(__name__)  # type: logging.Logger
logger.setLevel(logging.DEBUG)


class ROSProxy:
    """
    Provides access to a remote ROS master via XML-RPC.
    """
    def __init__(self,
                 shell: ShellProxy,
                 ws_host: str,
                 ip_address: str,
                 port: int = 11311
                 ) -> None:
        self.__shell: ShellProxy = shell
        self.__ws_host: str = ws_host
        self.__caller_id: str = '/rozzy'
        self.__port: int = port
        self.__ip_address: str = ip_address
        self.__uri: str = f"http://{ip_address}:{port}"
        logger.debug("connecting to ROS Master: %s", self.__uri)
        self.__connection = xmlrpc.client.ServerProxy(self.__uri)
        time.sleep(5)  # FIXME #1
        self.__parameters = ParameterServerProxy(self.__connection)
        self.__nodes: NodeManagerProxy = \
            NodeManagerProxy(self.__ip_address,
                             self.__connection,
                             self.__shell)
        self.__services: ServiceManagerProxy = \
            ServiceManagerProxy(self.__ip_address, self.__connection)

    @property
    def uri(self) -> str:
        """
        The URI of the ROS Master.
        """
        return self.__uri

    @property
    def nodes(self) -> NodeManagerProxy:
        """
        Provides access to the nodes running on this ROS master.
        """
        return self.__nodes

    @property
    def services(self) -> ServiceManagerProxy:
        """
        Provides access to the services advertised on this ROS master.
        """
        return self.__services

    @property
    def parameters(self) -> ParameterServerProxy:
        """
        Provides access to the parameter server for this ROS Master.
        """
        return self.__parameters

    @property
    def connection(self) -> xmlrpc.client.ServerProxy:
        """
        The XML-RPC connection to the ROS master.
        """
        return self.__connection

    @property
    def topic_to_type(self) -> Dict[str, str]:
        conn = self.connection
        code, msg, result = conn.getTopicTypes(self.__caller_id)
        if code != 1:
            raise RozzyException("bad API call!")
        return {name: typ for (name, typ) in result}

    def launch(self,
               *args: str,
               **kwargs: Union[int, str]
               ) -> None:
        """
        Provides an interface to roslaunch.
        """
        assert len(args) in [1, 2]
        launch_args = [f'{arg}:={val}' for arg, val in kwargs.items()]
        cmd = ' '.join(['roslaunch'] + list(args) + launch_args)
        self.__shell.non_blocking_execute(cmd)

    def record(self,
               fn: str,
               exclude_topics: Optional[Collection[str]] = None
               ) -> BagRecorderProxy:
        """
        Provides an interface to rosbag for recording ROS topics.
        """
        return BagRecorderProxy(fn,
                                self.__ws_host,
                                self.__shell,
                                self.__nodes,
                                exclude_topics=exclude_topics)


# TODO CoverageProxy
# - instrument: Python, C/C++
# - deinstrument
# - extract
# - flush