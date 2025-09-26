import json
import csv
import os
from datetime import datetime
from settings.config import Config

class ContactManager:
    """Менеджер для работы с контактами клиентов"""
    
    def __init__(self):
        self.contacts_file = "data/contacts.json"
        self.csv_file = "data/contacts.csv"
        self._ensure_data_directory()
    
    def _ensure_data_directory(self):
        """Создает папку data если ее нет"""
        os.makedirs("data", exist_ok=True)
    
    def save_contact(self, contact_data: dict):
        """Сохраняет контакт в JSON и CSV"""
        try:
            # Добавляем timestamp
            contact_data['timestamp'] = datetime.now().isoformat()
            contact_data['source'] = contact_data.get('source', 'manual')  # manual или contact_button
            
            # Сохраняем в JSON
            self._save_to_json(contact_data)
            
            # Сохраняем в CSV
            self._save_to_csv(contact_data)
            
            return True
        except Exception as e:
            print(f"Ошибка при сохранении контакта: {e}")
            return False
    
    def save_manual_contact(self, user_data: dict, contact_info: dict):
        """Сохраняет контакт, введенный вручную"""
        contact_data = {
            'first_name': contact_info.get('name') or user_data.get('first_name', ''),
            'last_name': user_data.get('last_name', ''),
            'phone_number': contact_info.get('phone', ''),
            'email': contact_info.get('email', ''),
            'username': user_data.get('username', 'не указан'),
            'user_id': user_data.get('user_id'),
            'additional_info': contact_info.get('additional_info', ''),
            'source': 'manual_text'
        }
        
        return self.save_contact(contact_data)
    
    def _save_to_json(self, contact_data: dict):
        """Сохраняет контакт в JSON файл"""
        contacts = []
        
        # Читаем существующие контакты
        if os.path.exists(self.contacts_file):
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                try:
                    contacts = json.load(f)
                except json.JSONDecodeError:
                    contacts = []
        
        # Добавляем новый контакт
        contacts.append(contact_data)
        
        # Сохраняем обратно
        with open(self.contacts_file, 'w', encoding='utf-8') as f:
            json.dump(contacts, f, ensure_ascii=False, indent=2)
    
    def _save_to_csv(self, contact_data: dict):
        """Сохраняет контакт в CSV файл"""
        file_exists = os.path.exists(self.csv_file)
        
        with open(self.csv_file, 'a', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # Записываем заголовок если файл новый
            if not file_exists:
                writer.writerow([
                    'Timestamp', 'First Name', 'Last Name', 'Phone', 
                    'Email', 'Username', 'User ID', 'Source', 'Additional Info'
                ])
            
            writer.writerow([
                contact_data['timestamp'],
                contact_data['first_name'],
                contact_data['last_name'],
                contact_data['phone_number'],
                contact_data['email'],
                contact_data['username'],
                contact_data['user_id'],
                contact_data.get('source', 'unknown'),
                contact_data.get('additional_info', '')
            ])
    
    def get_contacts_count(self) -> int:
        """Возвращает количество сохраненных контактов"""
        if os.path.exists(self.contacts_file):
            with open(self.contacts_file, 'r', encoding='utf-8') as f:
                try:
                    contacts = json.load(f)
                    return len(contacts)
                except json.JSONDecodeError:
                    return 0
        return 0