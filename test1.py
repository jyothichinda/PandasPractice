from flask import Flask,jsonify,request
import pandas as pd 

app = Flask(__name__)

# Try loading the CSV file and handle exceptions
try:
    data = pd.read_csv(r'C:/Users/Jyothirmayi/Downloads/origins.csv')
except FileNotFoundError:
    data = pd.DataFrame()  # Create an empty DataFrame if file is not found
    print("Error: CSV file not found at the specified path.")

@app.route("/")
def home():
    return "Welcome To Flask and Pandas DataFrame API"


@app.route("/create", methods=['GET'])
def create_dataframe():
    global df
    df = pd.DataFrame(data)
    return jsonify({"message":"DataFrame created successfully!","data":df.to_dict(orient="records")})

#using del method to delete data
@app.route("/delete", methods=['GET'])
def delete_dataframe():
    global df
    df = pd.DataFrame(data)
    try:
        del df
        return jsonify({"message":"DataFrame Deleted Successfully"})
    except NameError as e:
        return jsonify({"error":"DataFrame error"})
    
@app.route("/insert-row",methods=['POST'])
def insert_row():
    global df
    df = pd.DataFrame(data)
    new_row = request.get_json() 
    if not isinstance(new_row,dict):
        return jsonify({"error":"New row must be a dictionary"})
    new_row_df = pd.DataFrame([new_row])
    df = pd.concat([df, new_row_df],ignore_index = True)
    return jsonify({"message": "Row inserted successfully"}), 201

@app.route("/delete-row", methods=["DELETE"])
def delete_row():
    global df
    df = pd.DataFrame(data)
    delete_row = request.get_json()
    if "index" not in delete_row:
        return jsonify({"error": "Index key is required to delete a row"}), 400
    index_to_delete = delete_row["index"]
    if index_to_delete < 0 or index_to_delete >= len(df):
        return jsonify({"error": "Index out of range"}), 400
    df = df.drop(index=index_to_delete).reset_index(drop=True)
    return jsonify({"message": "Row deleted successfully", "updated_data": df.to_dict(orient="records")})


@app.route("/add-column",methods=["POST"])
def add_col():
    global df
    df = pd.DataFrame(data)
    new_col = request.get_json() 
    if not isinstance(new_col, dict):
        return jsonify({"error": "New column must be a dictionary"})
      # Extract column name and values
    if len(new_col) != 1:
        return jsonify({"error": "New column dictionary must have exactly one key-value pair"}), 400
    col_name, col_values = list(new_col.items())[0]
    # Ensure column values match the length of the existing DataFrame
    if not isinstance(col_values, list):
        return jsonify({"error": f"Column values must be a list of length {len(df)}"}), 400
    # Add the new column to the DataFrame
    df[col_name] = col_values
    return jsonify({"message": "Column added successfully", "updated_data": df.to_dict(orient="records")})

@app.route("/delete-col",methods=["DELETE"])
def del_col():
    global df
    df = pd.DataFrame(data)
    print(request.get_json())
    #takes input as an array
    updated_cols= request.get_json()
    #delete multiple columns
    #read input as an array of keys to be deleted
    if "columns" not in updated_cols or not isinstance(updated_cols["columns"],list):
        return jsonify({"error":"column name is required to delete"}) , 400
    column_to_delete =  updated_cols["columns"]
    missing_cols = [col for col in column_to_delete if col not in df.columns]
    if missing_cols:
        return jsonify({"error":f"Columns '{column_to_delete}' does not exist"}), 401
    df = df.drop(columns=column_to_delete)

    return jsonify({"message":f"Columns '{column_to_delete}' is deleted",'updated_data':df.to_dict(orient="records")})


# Ensure the app runs when this script is executed
if __name__ == "__main__":
    app.run(debug=True)

