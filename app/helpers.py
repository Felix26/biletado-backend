
class Helpers:

    def getDatabaseReady():
        # simulate failure by throwing an exception
        raise Exception("Database not reachable")

        return True # TODO: Test with real database