import logging

logger = logging.getLogger(__name__)


class Router:
    def __init__(self):
        self._exact = {}
        self._prefix = []

    def exact(self, path, handler):
        self._exact[path] = handler
        return handler

    def prefix(self, prefix, handler, param=None):
        self._prefix.append((prefix, handler, param))
        return handler

    def match(self, path):
        if path in self._exact:
            logger.debug("Exact match for %s", path)
            return self._exact[path], {}

        for prefix, handler, param in self._prefix:
            if path.startswith(prefix):
                params = {}
                if param is not None:
                    params[param] = path[len(prefix) :]
                logger.debug("Prefix match for %s -> %s", path, prefix)
                return handler, params

        logger.debug("No route matched for %s", path)
        return None, {}
