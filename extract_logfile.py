"""
Functions used to extract Nektar log file information
"""


def filter_lines(tag, lines):
    """
    Instance method to filter lines with a given tag like:
    #"TIMESTEP", "CFL:", "Steps:", "IO_INFOSTEPS"
    @param tag (str): string to look for. Eg. "TIMESTEP", "CFL:", "Steps:", "IO_INFOSTEPS"
    @return: No return - only self.filtered_lines updated
    """
    filtered_lines = []
    tag = tag
    for line in lines:
        line = line.strip()
        if line.startswith(tag):
            filtered_lines.append(line)

    return filtered_lines


def extract_timings_table(lines, inputlist_regions=None, list_cols=None):
    """
    Instance method to extract the summary timings table
    at the end of the Nektar simulation.
    @param inputlist_regions (list): List of strings containing keywords
      to extract from the table
        example: ['Execute', 'Pressure Solve', 'Viscous Solve']
    @return (list): list of dictionaries containing each row of the table
    """

    # specifying the rows and columns needed
    if inputlist_regions is None:
        list_regions = ["Execute", "Pressure Solve", "Viscous Solve"]
    else:
        list_regions = inputlist_regions

    # define the total number of columns by splitting the line which includes 'Execute'
    filtered_lines = filter_lines(inputlist_regions[0], lines)
    length = len(list_cols)

    # populating the list of dictionaries containing the table information
    lsdict_timings = []  # list to be populated
    # loop for timings to be found
    for region in list_regions:
        # initialise data holders
        dict_numbers = {}
        filtered_lines = []
        # filter lines according to regions
        filtered_lines = filter_lines(region, lines)
        dict_numbers["Region"] = region
        #             print(filtered_lines)

        if filtered_lines != []:  # if rows are found
            numbers = filtered_lines[0].split()[
                :length
            ]  # to get the same columns that exist in the Execute line
            # populate the keys from the columns in the table
            for i in range(1, length):
                dict_numbers[list_cols[i].strip()] = float(numbers[i])
        else:
            for i in range(1, length):
                dict_numbers[list_cols[i].strip()] = None

        lsdict_timings.append(dict_numbers)

    return lsdict_timings


def getvalue_from_CSV(df, filter_column, filter_value, plot_column):
    """
    filepath: path to a CSV file containing tabular data
    filter_column: column that you want to filter on
    filter_value: rows to filter for that column
    plot_column: columns to be plotted for the filtered rows
    """
    entry = df[df[filter_column] == filter_value][plot_column].values[0]
    return entry
