import pandas as pd
import numpy as np
import re
import warnings # Needed to silence the date warnings
from sklearn.preprocessing import LabelEncoder, OneHotEncoder, StandardScaler, MinMaxScaler
from sklearn.impute import SimpleImputer
from sklearn.utils import resample

class AdvancedProcessor:
    def __init__(self, df, config):
        self.df = df.copy()
        self.config = config
        self.log = [] 

    def add_log(self, message):
        self.log.append(message)

    def process(self):
        self.add_log("🚀 Starting advanced pipeline...")

        # --- 1. Date/Time Extraction ---
        if self.config.get('datetime', {}).get('enable'):
            self._handle_datetime()

        # --- 2. Text Cleaning ---
        if self.config.get('text_clean', {}).get('enable'):
            self._handle_text_cleaning()

        # --- 3. Missing Values ---
        if self.config['missing_values']['enable']:
            self._handle_missing(self.config['missing_values'])

        # --- 4. Outliers ---
        if self.config['outliers']['enable']:
            self._handle_outliers(self.config['outliers'])

        # --- 5. Encoding ---
        if self.config['encoding']['enable']:
            self._handle_encoding(self.config['encoding'])

        # --- 6. Scaling ---
        if self.config['scaling']['enable']:
            self._handle_scaling(self.config['scaling'])

        # --- 7. Balancing ---
        if self.config['balancing']['enable'] and self.config.get('target_col'):
            self._handle_balancing(self.config['balancing'])

        self.add_log("✅ Pipeline completed successfully.")
        return self.df, self.log

    # ==========================
    # FEATURE ENGINEERING
    # ==========================
    
    def _handle_datetime(self):
        """
        Auto-detects date columns and expands them into Year, Month, Day, Weekday.
        """
        cat_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in cat_cols:
            try:
                # FIX: Suppress the "Could not infer format" warning
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore")
                    # Try converting to datetime (coerce errors to NaT)
                    temp_series = pd.to_datetime(self.df[col], errors='coerce')
                
                # Heuristic: If > 80% of rows are valid dates, treat as Date Column
                if temp_series.notna().mean() > 0.8:
                    self.df[col] = temp_series
                    
                    # Extract Features
                    self.df[f'{col}_Year'] = self.df[col].dt.year
                    self.df[f'{col}_Month'] = self.df[col].dt.month
                    self.df[f'{col}_Day'] = self.df[col].dt.day
                    self.df[f'{col}_Weekday'] = self.df[col].dt.weekday 
                    
                    # Drop original date col
                    self.df.drop(columns=[col], inplace=True)
                    self.add_log(f"Extracted Date Features from '{col}' (Year, Month, Day).")
            except Exception:
                pass 

    def _handle_text_cleaning(self):
        """
        Basic NLP: Lowercases and removes special characters from text columns.
        """
        text_cols = self.df.select_dtypes(include=['object']).columns
        
        for col in text_cols:
            # Skip if it looks like a category (< 20 unique values)
            if self.df[col].nunique() < 20: 
                continue
                
            # Apply cleaning: Lowercase + Remove special chars
            self.df[col] = self.df[col].astype(str).apply(lambda x: re.sub(r'[^\w\s]', '', x.lower()))
            self.add_log(f"Cleaned text in column '{col}' (Lowercase + Removed Punctuation).")

    # ==========================
    # STANDARD CLEANING
    # ==========================

    def _handle_missing(self, cfg):
        strategy = cfg['strategy'] 
        
        if strategy == 'drop':
            init_len = len(self.df)
            self.df.dropna(inplace=True)
            self.add_log(f"Dropped {init_len - len(self.df)} rows with missing values.")
            return

        num_cols = self.df.select_dtypes(include=np.number).columns
        cat_cols = self.df.select_dtypes(exclude=np.number).columns

        if len(num_cols) > 0:
            if strategy in ['mean', 'median']:
                imputer = SimpleImputer(strategy=strategy)
                self.df[num_cols] = imputer.fit_transform(self.df[num_cols])
                self.add_log(f"Imputed numerical columns using '{strategy}'.")
        
        if len(cat_cols) > 0:
            imputer_cat = SimpleImputer(strategy='most_frequent')
            self.df[cat_cols] = imputer_cat.fit_transform(self.df[cat_cols])
            self.add_log(f"Imputed categorical columns using 'mode'.")

    def _handle_outliers(self, cfg):
        method = cfg['method'] 
        treatment = cfg['treatment'] 
        target = self.config.get('target_col')
        
        num_cols = self.df.select_dtypes(include=np.number).columns
        
        for col in num_cols:
            if target and col == target: continue 

            if method == 'iqr':
                Q1 = self.df[col].quantile(0.25)
                Q3 = self.df[col].quantile(0.75)
                IQR = Q3 - Q1
                lower = Q1 - 1.5 * IQR
                upper = Q3 + 1.5 * IQR
            elif method == 'z-score':
                mean = self.df[col].mean()
                std = self.df[col].std()
                lower = mean - 3 * std
                upper = mean + 3 * std

            if treatment == 'cap':
                self.df[col] = np.where(self.df[col] > upper, upper, self.df[col])
                self.df[col] = np.where(self.df[col] < lower, lower, self.df[col])
            elif treatment == 'trim':
                self.df = self.df[(self.df[col] >= lower) & (self.df[col] <= upper)]
        
        self.add_log(f"Handled outliers using {method} method ({treatment}).")

    def _handle_encoding(self, cfg):
        method = cfg['method'] 
        cat_cols = self.df.select_dtypes(include=['object', 'category']).columns
        
        if len(cat_cols) == 0: return

        if method == 'label':
            le = LabelEncoder()
            for col in cat_cols:
                self.df[col] = self.df[col].astype(str)
                self.df[col] = le.fit_transform(self.df[col])
            self.add_log("Applied Label Encoding to all categorical columns.")
            
        elif method == 'one-hot':
            self.df = pd.get_dummies(self.df, columns=cat_cols, drop_first=True)
            self.add_log("Applied One-Hot Encoding (dummies) to categorical columns.")

    def _handle_scaling(self, cfg):
        method = cfg['method'] 
        target = self.config.get('target_col')
        num_cols = self.df.select_dtypes(include=np.number).columns
        
        if target and target in num_cols:
             num_cols = num_cols.drop(target)

        if len(num_cols) == 0: return

        if method == 'standard':
            scaler = StandardScaler()
        else:
            scaler = MinMaxScaler()
            
        self.df[num_cols] = scaler.fit_transform(self.df[num_cols])
        self.add_log(f"Scaled features using {method} scaler.")

    def _handle_balancing(self, cfg):
        target = self.config.get('target_col')
        if not target: return
        
        maj_class_count = self.df[target].value_counts().max()
        classes = self.df[target].unique()
        df_list = []
        for cls in classes:
            df_cls = self.df[self.df[target] == cls]
            if len(df_cls) < maj_class_count:
                df_cls = resample(df_cls, replace=True, n_samples=maj_class_count, random_state=42)
            df_list.append(df_cls)
        
        self.df = pd.concat(df_list).sample(frac=1, random_state=42).reset_index(drop=True)
        self.add_log("Balanced dataset using Oversampling.")