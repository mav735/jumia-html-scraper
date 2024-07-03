class Converter:
    """
    Class for converting from html to markdown format
    """
    def __init__(self, main_block):
        self.main_block = main_block

    @staticmethod
    def table_to_markdown(table):
        """
        Converts a BeautifulSoup <table> element to Markdown format.

        Parameters
        ----------
        table : BeautifulSoup.Tag
            The <table> element to convert.

        Returns
        -------
        str
            Markdown formatted table.
        """
        headers = []
        rows = []

        # Extract headers
        header_row = table.find('thead').find('tr')
        for th in header_row.find_all('th'):
            headers.append(th.text.strip())

        # Extract rows
        for tr in table.find('tbody').find_all('tr'):
            row = []
            for td in tr.find_all('td'):
                row.append(td.text.strip())
            rows.append(row)

        # Format as Markdown table
        md_table = '| ' + ' | '.join(headers) + ' |\n'
        md_table += '| ' + ' | '.join(['---'] * len(headers)) + ' |\n'
        for row in rows:
            md_table += '| ' + ' | '.join(row) + ' |\n'

        return md_table

    @staticmethod
    def ul_to_markdown(ul):
        """
        Converts a BeautifulSoup <ul> element to Markdown format.

        Parameters
        ----------
        ul : BeautifulSoup.Tag
            The <ul> element to convert.

        Returns
        -------
        str
            Markdown formatted list.
        """
        items = []

        for li in ul.find_all('li'):
            items.append(f"- {li.text.strip()}")

        return '\n'.join(items)

    @staticmethod
    def ol_to_markdown(ol):
        """
        Converts a BeautifulSoup <ol> element to Markdown format.

        Parameters
        ----------
        ol : BeautifulSoup.Tag
            The <ol> element to convert.

        Returns
        -------
        str
            Markdown formatted ordered list.
        """
        items = []

        for index, li in enumerate(ol.find_all('li')):
            items.append(f"{index + 1}. {li.text.strip()}")

        return '\n'.join(items)

    @staticmethod
    def blockquote_to_markdown(blockquote):
        """
        Converts a BeautifulSoup <blockquote> element to Markdown format.

        Parameters
        ----------
        blockquote : BeautifulSoup.Tag
            The <blockquote> element to convert.

        Returns
        -------
        str
            Markdown formatted blockquote.
        """
        lines = []

        for line in blockquote.stripped_strings:
            lines.append(f"> {line}")

        return '\n'.join(lines)

    def main_block_to_markdown(self):
        """
        Converts a BeautifulSoup <div> element with mixed text and nested elements to Markdown format.

        Returns
        -------
        str
            Markdown formatted text.
        """
        result = []

        # Process each child element of the <div>
        for child in self.main_block.children:
            # Check if child is a string (text)
            if isinstance(child, str):
                # Append the text directly
                result.append(child.strip())
                result.append('\n\n')
            elif child.name == 'p':
                result.append(child.text.strip())
                result.append('\n\n')
            elif child.name in ['h1', 'h2', 'h3', 'h4', 'h5', 'h6']:
                result.append(f"{'#' * int(child.name[1])} {child.text.strip()}")
                result.append('\n\n')
            elif child.name == 'table':
                result.append(self.table_to_markdown(child))
                result.append('\n\n')
            elif child.name == 'ul':
                result.append(self.ul_to_markdown(child))
                result.append('\n\n')
            elif child.name == 'ol':
                result.append(self.ol_to_markdown(child))
                result.append('\n\n')
            elif child.name == 'blockquote':
                result.append(self.blockquote_to_markdown(child))
                result.append('\n\n')
            # Add more conditions for other elements as needed
            # Example: Handle <div>, <a>, <img>, etc.

        return ''.join(result)
