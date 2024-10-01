import pandas as pd
import os

class PriceListAnalyzer:
    def __init__(self, directory):
        self.directory = directory
        self.data = pd.DataFrame()

    def load_prices(self):
        name_columns = ['название', 'продукт', 'товар', 'наименование']
        price_columns = ['цена', 'розница']
        weight_columns = ['фасовка', 'масса', 'вес']

        files = [f for f in os.listdir(self.directory) if 'price' in f]
        for file in files:
            file_path = os.path.join(self.directory, file)
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read().splitlines()

                headers = content[0].split(',')

                rows = [line.split(',') for line in content[1:]]
                df = pd.DataFrame(rows, columns=headers)

                name_col = next((col for col in headers if col.strip() in name_columns), None)
                price_col = next((col for col in headers if col.strip() in price_columns), None)
                weight_col = next((col for col in headers if col.strip() in weight_columns), None)

                if name_col and price_col and weight_col:
                    df_filtered = df[[name_col, price_col, weight_col]].copy()
                    df_filtered.columns = ['name', 'price', 'weight']
                    df_filtered['price_per_kg'] = df_filtered['price'].astype(float) / df_filtered['weight'].astype(float)
                    df_filtered['file'] = file
                    self.data = pd.concat([self.data, df_filtered])
                else:
                    print(f"Не удалось найти нужные столбцы в файле {file}")
            except Exception as e:
                print(f"Ошибка при обработке файла {file}: {e}")

    def find_text(self, query):
        result = self.data[self.data['name'].str.contains(query, case=False, na=False)]
        result = result.sort_values(by='price_per_kg')
        return result

    def interactive_search(self):
        while True:
            query = input("Введите текст для поиска или 'exit' для выхода: ")
            if query.lower() == 'exit':
                print("Работа завершена.")
                break
            results = self.find_text(query)
            if not results.empty:
                print("№  Наименование                Цена    Вес    Файл             Цена за кг.")
                for i, row in results.iterrows():
                    print(f"{i+1:<3} {row['name']:<25} {row['price']:<6} {row['weight']:<6} {row['file']:<15} {row['price_per_kg']:<10.2f}")
            else:
                print("Ничего не найдено.")

    def export_to_html(self, output_file):
        if not self.data.empty:
            self.data.to_html(output_file, index=False, escape=False)
            print(f"Данные успешно экспортированы в {output_file}.")
        else:
            print("Нет данных для экспорта.")


analyzer = PriceListAnalyzer('catalog')
analyzer.load_prices()
analyzer.interactive_search()
analyzer.export_to_html('prices_output.html')
