import re

class HelperMethods:

    @staticmethod
    def convert_for_word_search_mysql(x: str) -> tuple[str, list[str]]:
        """
        Removes all letters that aren't alphanumerical or underscore and strips spaces. 

        Args:
            name (str): Name of categories.

        Returns:
            str: Each word separated by spaces and has + at start and * at the end. For example '+red* +apple*'
            list[str]: Each word containg only `\w`.
        """
        # keep only \w
        x = re.sub(r'\W', ' ', x)
        x = x.strip()
        if len(x) == 0:
            return '', []
        x = re.split(r'\s+', x)
        # + means the word must be present and * match any other characters after the word
        # for full text search in mysql
        x_str = [f'+{v}*' for v in x]
        x_str = ' '.join(x_str)
        return x_str, x
