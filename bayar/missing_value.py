# 1. Binary Missing Value Feature
def add_binary_missing_features(dataframe, cols=[]):
    temp = dataframe.copy()
    if len(cols) > 0:
        temp = temp[cols]
    temp = temp.isnull().astype("int8")
    new_cols = list(map(lambda x: "ISNA_" + str(x).upper(), temp.columns))
    dataframe[new_cols] = temp
    return dataframe

# 2. How many missing values are there in each rows?
def add_numofmissing_rows(dataframe):
    dataframe["NUMOF_NA_COLS"] = dataframe.isnull().sum(axis=1)


# 3. Did Missing Values fill with any summary stats?
def filled_columns(dataframe):
    # Select Numerical Features
    temp = dataframe.select_dtypes(["float", "integer"])

    filled = []

    for i in temp.columns:
        if (temp[i].mode() == temp[i].median())[0]:
            method = "median"
        elif (temp[i].mode() == temp[i].mean())[0]:
            method = "mean"
        else:
            method = "not fill or unknown"

        filled.append(pd.DataFrame({"Feature": [i], "Filling Method": [method]}))
    filled = pd.concat(filled)
    filled = filled[filled["Filling Method"] != "not fill or unknown"].reset_index(drop=True)

    print("# Might missing values be filling with any summary stats?")
    print("--------------------------------------------------------------")
    if len(filled) == 0:
        print("There is no matching for any filling methods!")
    else:
        print("There are some matching for any fillings methods below!")
        print("You should check the distributions of these features!")
        print("-------------------------------------------------------------- \n")
        return filled

# 4. Possible Fillings
def possible_fillings(dataframe):
    temp = dataframe.copy()
    for i in temp.columns:
        if temp[i].dtype == "int" or temp[i].dtype == "float":
            temp[i] = np.where(dataframe[i] <= -99999, "-99999 (and less)", temp[i])
            temp[i] = np.where(dataframe[i] == -1, "-1", temp[i])
            temp[i] = np.where(dataframe[i].isin([99, -99]), "+/-99", temp[i])
            temp[i] = np.where(dataframe[i].isin([999, -999]), "+/-999", temp[i])
        else:
            temp[i].replace(r'^\s*$', 'Empty strings', regex=True, inplace=True)
        temp[i] = np.where(dataframe[i].isnull(), "NA values", temp[i])
    temp = pd.melt(temp).rename({"variable": "Features", "value": "Possible Fillings"}, axis=1)
    temp = temp[
        temp["Possible Fillings"].isin(["-99999 (and less)", "NA values", "-1", "+/-99", "+/-999", "Empty strings"])]

    if len(temp) > 0:
        temp = pd.pivot_table(temp.reset_index(), index="Features", columns="Possible Fillings", aggfunc="count",
                              fill_value=0)
        return temp
    else:
        print("There is no matching for possible fillings!")


# 5. Missing No Plots
def missingno_plots(dataframe, plot_type="heatmap"):
    if plot_type == "matrix":
        msno.matrix(dataframe)
        plt.show()
    elif plot_type == "heatmap":
        msno.heatmap(dataframe)
        plt.show()
    elif plot_type == "dendrogram":
        msno.dendrogram(dataframe)
        plt.show()
    else:
        print("Please, choose a valid plot type! For example: 'heatmap', 'matrix' or 'dendrogram'")

# 6. Plot Missing
def plot_missing(dataframe):
    temp = pd.DataFrame({"Missing": dataframe.isnull().sum()}).reset_index()
    temp["Actual"] = len(dataframe) - temp["Missing"]
    temp = pd.melt(temp, id_vars="index")

    ggplot(temp, aes(x="index", y="value", fill="variable")) + \
    geom_col(position="fill") + \
    coord_flip() + \
    labs(title="Percentage of missing values", fill="",
         x='Variable', y="% of missing values") + \
    scale_y_continuous(labels=["0", "25", "50", "75", "100"]) + \
    scale_fill_manual(values=["slategray", "royalblue"])
    plt.show()

# 7. Table Missing
def table_missing(data):

    """
        This function creates a dataframe for missing value stats each variables.

        Parameters
        ----------

        data: dataframe
            dataframe that include variables

        Returns
        ----------
        dataframe or string
    """

    mst = pd.DataFrame(
        {"Num_Missing": data.isnull().sum(), "Missing_Ratio": data.isnull().sum() / data.shape[0]}).sort_values(
        "Num_Missing", ascending=False)
    mst["DataTypes"] = data[mst.index].dtypes.values
    mst = mst[mst.Num_Missing > 0].reset_index().rename({"index": "Feature"}, axis=1)

    if len(mst) > 0:
        print("How many variables include missing value?:", mst.shape[0], "\n")
        return mst
    else:
        print("There are no missing values in any of variables")
