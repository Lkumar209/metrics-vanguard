# src/models/transfer_predictor.py
class TransferPredictor:
    def __init__(self):
        self.model = tf.keras.Sequential([
            tf.keras.layers.Dense(128, activation='relu'),
            tf.keras.layers.Dropout(0.2),
            tf.keras.layers.Dense(64, activation='relu'),
            tf.keras.layers.Dense(5, activation='softmax')  # Top 5 likely destinations
        ])
    
    def predict_next_club(self, player_features):
        # Predict most likely next clubs
        pass
