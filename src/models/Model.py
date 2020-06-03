class Model():
    def getUser(self, userName):
        """
        Retrieves the user from database.
        :param userName: name of the user to be retrieved
        :returns: undefined if the user is not found in the database. User object if it is.
        :raises: Databse errors on connection and insertion
        """
        pass

    def insertUser(self, user):
        """
        Inserts proccessed user information into the database for future access.
        :param user: user object with proccessed fields
        :returns: nothing
        :raises: Databse errors on connection and insertion
        """
        pass
