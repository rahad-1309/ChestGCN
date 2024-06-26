# -*- coding: utf-8 -*-

import os
import pandas as pd
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
import tensorflow as tf
from tensorflow import keras
from tensorflow.keras import layers

from google.colab import drive
drive.mount('/content/drive')

papers = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/feature_extraction.csv')
print("Papers shape:", papers.shape)

import pandas as pd

# Load the CSV file into a Pandas dataframe
df = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/feature_extraction.csv')

# Add a new column with a specified value
new_col_value = 0
df['COVID'] = new_col_value

df.head(10)

df.columns

import pandas as pd

# Load the CSV file into a Pandas dataframe
df2 = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/feature_extraction_Tuberculosis.csv')

# Add a new column with a specified value
new_col_value = 1
df2['Tuberculosis'] = new_col_value

df2.head(10)

df2.columns

import pandas as pd

# Load the CSV file into a Pandas dataframe
df3 = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/feature_extraction_normal.csv')

# Add a new column with a specified value
new_col_value = 2
df3['normal'] = new_col_value

df3.head(10)

df3.columns

import pandas as pd

# Load the CSV file into a Pandas dataframe
df4 = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/feature_extraction_pneumonia.csv')

# Add a new column with a specified value
new_col_value = 3
df4['Pneumonia'] = new_col_value

df4.head(10)

df4.columns

df_m = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/Two_Merged feature_extraction_Covid - feature_extraction - Merged feature_extraction_Covid - feature_extraction.csv')
df_m.shape

df_m.head()

df_g2 = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/Feature - Sheet1.csv')
df_g2.head()

class_values = sorted(df_m["Class"].unique())
class_idx = {name: id for id, name in enumerate(class_values)}
paper_idx = {name: idx for idx, name in enumerate(sorted(df_g2["node"].unique()))}
print(paper_idx)

train_data, test_data = [], []

for _, group_data in df_m.groupby("Class"):
    # Select around 50% of the dataset for training.
    random_selection = np.random.rand(len(group_data.index)) <= 0.5
    train_data.append(group_data[random_selection])
    test_data.append(group_data[~random_selection])

train_data = pd.concat(train_data).sample(frac=1)
test_data = pd.concat(test_data).sample(frac=1)

print("Train data shape:", train_data.shape)
print("Test data shape:", test_data.shape)

hidden_units = [32, 32]
learning_rate = 0.01
dropout_rate = 0.5
num_epochs = 50
batch_size = 256

def run_experiment(model, x_train, y_train):
    # Compile the model.
    model.compile(
        optimizer=keras.optimizers.Adam(learning_rate),
        loss=keras.losses.SparseCategoricalCrossentropy(from_logits=True),
        metrics=[keras.metrics.SparseCategoricalAccuracy(name="acc")],
    )
    # Create an early stopping callback.
    early_stopping = keras.callbacks.EarlyStopping(
        monitor="val_acc", patience=50, restore_best_weights=True
    )
    # Fit the model.
    history = model.fit(
        x=x_train,
        y=y_train,
        epochs=num_epochs,
        batch_size=batch_size,
        validation_split=0.15,
        callbacks=[early_stopping],
    )

    return history

def display_learning_curves(history):
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))

    ax1.plot(history.history["loss"])
    ax1.plot(history.history["val_loss"])
    ax1.legend(["train", "test"], loc="upper right")
    ax1.set_xlabel("Epochs")
    ax1.set_ylabel("Loss")

    ax2.plot(history.history["acc"])
    ax2.plot(history.history["val_acc"])
    ax2.legend(["train", "test"], loc="upper right")
    ax2.set_xlabel("Epochs")
    ax2.set_ylabel("Accuracy")
    plt.show()

def create_ffn(hidden_units, dropout_rate, name=None):
    fnn_layers = []

    for units in hidden_units:
        fnn_layers.append(layers.BatchNormalization())
        fnn_layers.append(layers.Dropout(dropout_rate))
        fnn_layers.append(layers.Dense(units, activation=tf.nn.gelu))

    return keras.Sequential(fnn_layers, name=name)

feature_names = set(df_m.columns)
num_features = len(feature_names)
num_classes = len(class_idx)

# Create train and test features as a numpy array.
x_train = train_data[feature_names].to_numpy()
x_test = test_data[feature_names].to_numpy()
# Create train and test targets as a numpy array.
y_train = train_data["Class"]
y_test = test_data["Class"]

def create_baseline_model(hidden_units, num_classes, dropout_rate=0.2):
    inputs = layers.Input(shape=(num_features,), name="input_features")
    x = create_ffn(hidden_units, dropout_rate, name=f"ffn_block1")(inputs)
    for block_idx in range(4):
        # Create an FFN block.
        x1 = create_ffn(hidden_units, dropout_rate, name=f"ffn_block{block_idx + 2}")(x)
        # Add skip connection.
        x = layers.Add(name=f"skip_connection{block_idx + 2}")([x, x1])
    # Compute logits.
    logits = layers.Dense(num_classes, name="logits")(x)
    # Create the model.
    return keras.Model(inputs=inputs, outputs=logits, name="baseline")


baseline_model = create_baseline_model(hidden_units, num_classes, dropout_rate)
baseline_model.summary()

history = run_experiment(baseline_model, x_train, y_train)

display_learning_curves(history)

_, test_accuracy = baseline_model.evaluate(x=x_test, y=y_test, verbose=0)
print(f"Test accuracy: {round(test_accuracy * 100, 2)}%")

import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Load the features from a CSV file
df_g = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/Two_Merged feature_extraction_Covid - feature_extraction - Merged feature_extraction_Covid - feature_extraction.csv')

# Normalize the feature values
df_norm = (df_g - df_g.mean()) / df_g.std()

# Compute the correlation matrix
corr_matrix = df_norm.corr()

pd.plotting.register_matplotlib_converters()
import matplotlib.pyplot as plt
import seaborn as sns

plt.style.use("seaborn-whitegrid")

plt.figure(figsize = (10,7))
sns.heatmap(df_g.corr(), annot=True, cmap="Blues")
plt.title('Absolute Pearson Correlation between Different Features')

# Step 2: Create a list of nodes from the column names in the DataFrame
node_features = list(df_g.columns)

# Step 3: Create a list of edges from the data in the DataFrame
edges = []
for i, col1 in enumerate(df_g.columns):
    for j, col2 in enumerate(df_g.columns):
        if i < j:
          edges.append((col1, col2))
            #corr = df_g[col1].corr(df_g[col2])
           # if abs(corr) >= 0.45:  # Threshold for significant correlation


edge_weights = edges
graph_info = (node_features, edges, edge_weights)

print(edges)

# Step 2: Create a list of nodes from the column names in the DataFrame
nodes = list(df_g.columns)

# Step 3: Create a list of edges from the data in the DataFrame
edges = []
for i, col1 in enumerate(df_g.columns):
    for j, col2 in enumerate(df_g.columns):
        if i < j:
          edges.append((col1, col2))
           # corr = df_g[col1].corr(df_g[col2])
            #if abs(corr) >= 0.5:  # Threshold for significant correlation


# Step 4: Create a NetworkX graph object and add the nodes and edges to it
G = nx.Graph()
G.add_nodes_from(nodes)
G.add_edges_from(edges)

# Step 5: Draw the graph using a layout algorithm and save or show the figure
pos = nx.spring_layout(G, seed=42) # Using seed for reproducibility
fig, ax = plt.subplots(figsize=(20, 20))
nx.draw_networkx(G, pos, with_labels=True, node_size=1000, ax=ax, font_size=15)
edge_labels = {(u, v): f'{df_g[u].corr(df_g[v]):.2f}' for u, v in G.edges()}
nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=15, ax=ax)
#nx.draw_networkx_edge_labels(G, pos, edge_labels=edge_labels, font_size=15, ax=ax)
plt.axis('off')
plt.show()

print(nodes)
print(edges)

df_g2 = pd.read_csv('/content/drive/MyDrive/SER_preprocessing/feature_extraction/CSV/Feature - Sheet1.csv')

edges = df_g2[["source", "target"]].to_numpy().T
# Create an edge weights array of ones.
edge_weights = tf.ones(shape=edges.shape[1])
# Create a node features array of shape [num_nodes, num_features].
node_features = tf.cast(
    df_g.sort_values("Class")[feature_names].to_numpy(), dtype=tf.dtypes.float32
)
# Create graph info tuple with node_features, edges, and edge_weights.
graph_info = (node_features, edges, edge_weights)

print("Edges shape:", edges.shape)
print("Nodes shape:", node_features.shape)

class GraphConvLayer(layers.Layer):
    def __init__(
        self,
        hidden_units,
        dropout_rate=0.2,
        aggregation_type="mean",
        combination_type="concat",
        normalize=False,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        self.aggregation_type = aggregation_type
        self.combination_type = combination_type
        self.normalize = normalize

        self.ffn_prepare = create_ffn(hidden_units, dropout_rate)
        if self.combination_type == "gated":
            self.update_fn = layers.GRU(
                units=hidden_units,
                activation="tanh",
                recurrent_activation="sigmoid",
                dropout=dropout_rate,
                return_state=True,
                recurrent_dropout=dropout_rate,
            )
        else:
            self.update_fn = create_ffn(hidden_units, dropout_rate)

    def prepare(self, node_repesentations, weights=None):
        # node_repesentations shape is [num_edges, embedding_dim].
        messages = self.ffn_prepare(node_repesentations)
        if weights is not None:
            messages = messages * tf.expand_dims(weights, -1)
        return messages

    def aggregate(self, node_indices, neighbour_messages, node_repesentations):
        # node_indices shape is [num_edges].
        # neighbour_messages shape: [num_edges, representation_dim].
        # node_repesentations shape is [num_nodes, representation_dim]
        num_nodes = node_repesentations.shape[0]
        if self.aggregation_type == "sum":
            aggregated_message = tf.math.unsorted_segment_sum(
                neighbour_messages, node_indices, num_segments=num_nodes
            )
        elif self.aggregation_type == "mean":
            aggregated_message = tf.math.unsorted_segment_mean(
                neighbour_messages, node_indices, num_segments=num_nodes
            )
        elif self.aggregation_type == "max":
            aggregated_message = tf.math.unsorted_segment_max(
                neighbour_messages, node_indices, num_segments=num_nodes
            )
        else:
            raise ValueError(f"Invalid aggregation type: {self.aggregation_type}.")

        return aggregated_message

    def update(self, node_repesentations, aggregated_messages):
        # node_repesentations shape is [num_nodes, representation_dim].
        # aggregated_messages shape is [num_nodes, representation_dim].
        if self.combination_type == "gru":
            # Create a sequence of two elements for the GRU layer.
            h = tf.stack([node_repesentations, aggregated_messages], axis=1)
        elif self.combination_type == "concat":
            # Concatenate the node_repesentations and aggregated_messages.
            h = tf.concat([node_repesentations, aggregated_messages], axis=1)
        elif self.combination_type == "add":
            # Add node_repesentations and aggregated_messages.
            h = node_repesentations + aggregated_messages
        else:
            raise ValueError(f"Invalid combination type: {self.combination_type}.")

        # Apply the processing function.
        node_embeddings = self.update_fn(h)
        if self.combination_type == "gru":
            node_embeddings = tf.unstack(node_embeddings, axis=1)[-1]

        if self.normalize:
            node_embeddings = tf.nn.l2_normalize(node_embeddings, axis=-1)
        return node_embeddings

    def call(self, inputs):
        """Process the inputs to produce the node_embeddings.

        inputs: a tuple of three elements: node_repesentations, edges, edge_weights.
        Returns: node_embeddings of shape [num_nodes, representation_dim].
        """

        node_repesentations, edges, edge_weights = inputs
        # Get node_indices (source) and neighbour_indices (target) from edges.
        node_indices, neighbour_indices = edges[0], edges[1]
        # neighbour_repesentations shape is [num_edges, representation_dim].
        neighbour_repesentations = tf.gather(node_repesentations, neighbour_indices)

        # Prepare the messages of the neighbours.
        neighbour_messages = self.prepare(neighbour_repesentations, edge_weights)
        # Aggregate the neighbour messages.
        aggregated_messages = self.aggregate(
            node_indices, neighbour_messages, node_repesentations
        )
        # Update the node embedding with the neighbour messages.
        return self.update(node_repesentations, aggregated_messages)

class GNNNodeClassifier(tf.keras.Model):
    def __init__(
        self,
        graph_info,
        num_classes,
        hidden_units,
        aggregation_type="sum",
        combination_type="concat",
        dropout_rate=0.2,
        normalize=True,
        *args,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)

        # Unpack graph_info to three elements: node_features, edges, and edge_weight.
        node_features, edges, edge_weights = graph_info
        self.node_features = node_features
        self.edges = edges
        self.edge_weights = edge_weights
        # Set edge_weights to ones if not provided.
        if self.edge_weights is None:
            self.edge_weights = tf.ones(shape=edges.shape[1])
        # Scale edge_weights to sum to 1.
        self.edge_weights = self.edge_weights / tf.math.reduce_sum(self.edge_weights)

        # Create a process layer.
        self.preprocess = create_ffn(hidden_units, dropout_rate, name="preprocess")
        # Create the first GraphConv layer.
        self.conv1 = GraphConvLayer(
            hidden_units,
            dropout_rate,
            aggregation_type,
            combination_type,
            normalize,
            name="graph_conv1",
        )
        # Create the second GraphConv layer.
        self.conv2 = GraphConvLayer(
            hidden_units,
            dropout_rate,
            aggregation_type,
            combination_type,
            normalize,
            name="graph_conv2",
        )
        # Create a postprocess layer.
        self.postprocess = create_ffn(hidden_units, dropout_rate, name="postprocess")
        # Create a compute logits layer.
        self.compute_logits = layers.Dense(units=num_classes, name="logits")

    def call(self, input_node_indices):
        # Preprocess the node_features to produce node representations.
        x = self.preprocess(self.node_features)
        # Apply the first graph conv layer.
        x1 = self.conv1((x, self.edges, self.edge_weights))
        # Skip connection.
        x = x1 + x
        # Apply the second graph conv layer.
        x2 = self.conv2((x, self.edges, self.edge_weights))
        # Skip connection.
        x = x2 + x
        # Postprocess node embedding.
        x = self.postprocess(x)
        # Fetch node embeddings for the input node_indices.
        node_embeddings = tf.gather(x, input_node_indices)
        # Compute logits
        return self.compute_logits(node_embeddings)

gnn_model = GNNNodeClassifier(
    graph_info=graph_info,
    num_classes=num_classes,
    hidden_units=hidden_units,
    dropout_rate=dropout_rate,
    name="gnn_model",
)

print("GNN output shape:", gnn_model([1, 10, 100]))

gnn_model.summary()

x_train = train_data.Class.to_numpy()
history = run_experiment(gnn_model, x_train, y_train)

display_learning_curves(history)

x_test = test_data.Class.to_numpy()
_, test_accuracy = gnn_model.evaluate(x=x_test, y=y_test, verbose=0)
print(f"Test accuracy: {round(test_accuracy * 100, 2)}%")
