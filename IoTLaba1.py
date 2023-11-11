import sys
import datetime
from PySide6.QtWidgets import QApplication, QWidget, QVBoxLayout, QGridLayout, QLabel, QLineEdit, QPushButton, QRadioButton, QPlainTextEdit
from PySide6.QtCore import QTimer


class SmartThermostatApp(QWidget):
    def __init__(self):
        super().__init__()

        self.current_temperature = 28.0
        self.temperature_current_value = QLabel(str(self.current_temperature))
        self.desired_temperature = 22.0

        self.current_humidity = 20.0
        self.humidity_current_value = QLabel(str(self.current_humidity))
        self.desired_humidity = 50.0

        self.data_generation_time = 10000
        self.data_generation_time_edit = QLineEdit(str(self.data_generation_time/1000))

        self.current_power_conditioner_temperature = 0
        self.current_power_conditioner_temperature_value = QLabel(str(self.current_power_conditioner_temperature))

        self.current_power_conditioner_humidity = 0
        self.current_power_conditioner_humidity_value = QLabel(str(self.current_power_conditioner_humidity))

        self.automatic_radio = QRadioButton('Автоматический режим')
        self.manual_radio = QRadioButton('Ручной режим')

        self.log_output = QPlainTextEdit(self)
        self.log_output.setReadOnly(True)
        self.log_output.setPlaceholderText("Логи будут отображаться здесь.")
        self.log_output.setMaximumBlockCount(1000)

        self.timer_conditions = QTimer(self)
        self.timer_conditions.timeout.connect(self.update_conditions)
        self.timer_conditions.start(1000)  # Обновлять значения каждые 10 секунд

        self.timer_logs = QTimer(self)
        self.timer_logs.timeout.connect(self.update_logs)
        self.timer_logs.start(10000)

        self.init_ui()

    def init_ui(self):
        """Функция, необходимая для отрисовки оконного приложения на моменте инициализации"""
        temperature_current_label = QLabel(f'Температура(°C): ')
        self.desired_temperature_edit = QLineEdit(f'{self.desired_temperature}')

        humidity_current_label = QLabel(f'Влажность(%): ')
        self.desired_humidity_edit = QLineEdit(f'{self.desired_humidity}')

        current_power_conditioner_temperature_label = QLabel(f'Мощность кондиционера(Температура) (%)')
        self.desired_power_conditioner_temperature_edit = QLineEdit(f'{self.current_power_conditioner_temperature}')

        current_power_conditioner_humidity_label = QLabel(f'Мощность кондиционера(Влажность) (%)')
        self.desired_power_conditioner_humidity_edit = QLineEdit(f'{self.current_power_conditioner_humidity}')

        self.automatic_radio.setChecked(True)
        self.set_mode('Automatic')

        apply_button = QPushButton('Применить настройки')
        apply_button.clicked.connect(self.apply_settings)

        data_generation_time_label = QLabel(f'Время обновления логов (c):')

        grid_layout = QGridLayout()
        grid_layout.addWidget(QLabel('Текущая'), 0, 1)
        grid_layout.addWidget(QLabel('Настраиваемая'), 0, 2)
        grid_layout.addWidget(temperature_current_label, 1, 0)
        grid_layout.addWidget(self.temperature_current_value, 1, 1)
        grid_layout.addWidget(self.desired_temperature_edit, 1, 2)
        grid_layout.addWidget(humidity_current_label, 2, 0)
        grid_layout.addWidget(self.humidity_current_value, 2, 1)
        grid_layout.addWidget(self.desired_humidity_edit, 2, 2)
        grid_layout.addWidget(current_power_conditioner_temperature_label, 3, 0)
        grid_layout.addWidget(self.current_power_conditioner_temperature_value, 3, 1)
        grid_layout.addWidget(self.desired_power_conditioner_temperature_edit, 3, 2)
        grid_layout.addWidget(current_power_conditioner_humidity_label, 4, 0)
        grid_layout.addWidget(self.current_power_conditioner_humidity_value, 4, 1)
        grid_layout.addWidget(self.desired_power_conditioner_humidity_edit, 4, 2)

        mode_layout = QVBoxLayout()
        mode_layout.addWidget(self.automatic_radio)
        mode_layout.addWidget(self.manual_radio)

        data_generation_time_layout = QGridLayout()
        data_generation_time_layout.addWidget(data_generation_time_label, 0, 0)
        data_generation_time_layout.addWidget(self.data_generation_time_edit, 0, 1)

        layout = QVBoxLayout()
        layout.addLayout(grid_layout)
        layout.addLayout(mode_layout)
        layout.addWidget(apply_button)
        layout.addLayout(data_generation_time_layout)
        layout.addWidget(self.log_output)

        self.setLayout(layout)

        self.automatic_radio.toggled.connect(lambda: self.set_mode('Automatic'))
        self.manual_radio.toggled.connect(lambda: self.set_mode('Manual'))

        self.setWindowTitle('Умный термостат')
        self.setFixedSize(450, 600)
        self.show()

    def log(self, message):
        """Метод для добавления логов"""
        self.log_output.appendPlainText(message)

    def apply_settings(self):
        """Функция, реализующая логику кнопки 'Применить настройки' """
        if self.automatic_radio.isChecked():
            try:
                self.desired_temperature = float(self.desired_temperature_edit.text().split()[0])
                self.desired_humidity = float(self.desired_humidity_edit.text().split()[0])

                self.log(f'Настройки применены - Желаемая температура: {self.desired_temperature} °C, Желаемая влажность: {self.desired_humidity} %, Режим: {self.mode}')
            except ValueError:
                self.log('Неверный ввод. Пожалуйста, введите корректные числовые значения.')

        else:
            try:
                self.current_power_conditioner_temperature = float(self.desired_power_conditioner_temperature_edit.text().split()[0])
                self.current_power_conditioner_humidity = float(self.desired_power_conditioner_humidity_edit.text().split()[0])

                self.log(f'Настройки применены - Желаемая мощность кондиционера (температура): {self.current_power_conditioner_temperature}, Желаемая мощность кондиционера (влажность): {self.current_power_conditioner_humidity}, Режим: {self.mode}')
            except ValueError:
                self.log('Неверный ввод. Пожалуйста, введите корректные числовые значения.')

        self.timer_logs.start(float(self.data_generation_time_edit.text().split()[0])*1000)


    def set_mode(self, mode):
        """Функция, блокирующая изменение полей в зависимости от выбранного режима"""
        self.mode = mode

        self.desired_temperature_edit.setEnabled(mode == 'Automatic')
        self.desired_humidity_edit.setEnabled(mode == 'Automatic')
        self.desired_power_conditioner_temperature_edit.setEnabled(mode == 'Manual')
        self.desired_power_conditioner_humidity_edit.setEnabled(mode == 'Manual')

    def update_conditions(self):
        """Функция, которая задает неизменяемые значения на основе заданных изменяемых"""

        # Условная логика работы автоматического режима
        if self.automatic_radio.isChecked():
            if self.desired_temperature < self.current_temperature:
                self.current_power_conditioner_temperature = 60
            else:
                self.current_power_conditioner_temperature = 0

            if self.desired_humidity < self.current_humidity:
                self.current_power_conditioner_humidity = 60
            else:
                self.current_power_conditioner_humidity = 0


        temperature_increment = 0.1 # Если кондиционер выключен
        humidity_increment = 1 # Если кондиционер выключен

        # Условные формулы, описывающие поведение температуры и влажности от заданной мощности кондиционера.
        temperature_increment = temperature_increment - 0.002 * self.current_power_conditioner_temperature
        humidity_increment = humidity_increment - 0.02 * self.current_power_conditioner_humidity

        if 15 < self.current_temperature + temperature_increment < 40:
            self.current_temperature += temperature_increment

        if 0 < self.current_humidity + humidity_increment < 100:
            self.current_humidity += humidity_increment

        self.update_values()

    def update_values(self):
        """Функция, которая обновляет отображаемые значения в оконном приложении"""
        self.temperature_current_value.setText(f'{round(self.current_temperature, 1)}')
        self.humidity_current_value.setText(f'{round(self.current_humidity, 1)}')
        self.current_power_conditioner_temperature_value.setText(f'{round(self.current_power_conditioner_temperature)}')
        self.current_power_conditioner_humidity_value.setText(f'{round(self.current_power_conditioner_humidity)}')

        if self.automatic_radio.isChecked():
            self.desired_power_conditioner_temperature_edit.setText(f'{round(self.current_power_conditioner_temperature)}')
            self.desired_power_conditioner_humidity_edit.setText(f'{round(self.current_power_conditioner_humidity)}')

    def update_logs(self):
        """Функция, которая выводит логи раз в заданное время"""
        self.log(f'[{datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")}] Режим работы кондиционера: {self.mode}. Текущая температура: {round(self.current_temperature, 1)}. Текущая влажность: {round(self.current_humidity, 1)}. Текущая мощность кондиционера (Температура): {self.current_power_conditioner_temperature}. Текущая мощность кондиционера (Влажность): {self.current_power_conditioner_humidity}.')


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SmartThermostatApp()
    sys.exit(app.exec())
