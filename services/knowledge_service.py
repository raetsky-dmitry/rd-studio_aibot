import json
import os
import logging
from typing import Dict, List, Optional, Any

logger = logging.getLogger(__name__)

class KnowledgeService:
    """Сервис для работы с базой знаний"""
    
    def __init__(self):
        self.base_path = "knowledge_base"
        self.load_all_knowledge()
    
    def load_all_knowledge(self):
        """Загружает все данные из базы знаний"""
        try:
            # Загружаем цены
            with open(f"{self.base_path}/prices.json", 'r', encoding='utf-8') as f:
                self.prices = json.load(f)
            
            # Загружаем FAQ
            with open(f"{self.base_path}/faq.json", 'r', encoding='utf-8') as f:
                self.faq = json.load(f)
            
            # Загружаем услуги
            with open(f"{self.base_path}/services.json", 'r', encoding='utf-8') as f:
                self.services = json.load(f)
            
            # Загружаем информацию о компании
            with open(f"{self.base_path}/company_info.json", 'r', encoding='utf-8') as f:
                self.company_info = json.load(f)
            
            logger.info("База знаний успешно загружена")
            
        except Exception as e:
            logger.error(f"Ошибка при загрузке базы знаний: {e}")
            # Создаем пустые структуры в случае ошибки
            self.prices = {}
            self.faq = {}
            self.services = {}
            self.company_info = {}
    
    def get_prices_info(self) -> str:
        """Возвращает информацию о ценах в текстовом формате"""
        try:
            packages = self.prices.get('packages', [])
            additional_services = self.prices.get('additional_services', [])
            
            result = "💰 ПАКЕТЫ И ЦЕНЫ:\n\n"
            
            for package in packages:
                result += f"🎯 {package['name']}\n"
                result += f"💵 {package['price']}\n"
                result += f"⏱ {package['timeline']}\n"
                result += f"📝 {package['description']}\n"
                result += "Включает:\n"
                for feature in package['features']:
                    result += f"• {feature}\n"
                result += "\n"
            
            result += "🔧 ДОПОЛНИТЕЛЬНЫЕ УСЛУГИ:\n"
            for service in additional_services:
                result += f"• {service['name']}: {service['price']} - {service['description']}\n"
            
            result += "\n💳 УСЛОВИЯ ОПЛАТЫ:\n"
            for term in self.prices.get('payment_terms', []):
                result += f"• {term}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при формировании информации о ценах: {e}")
            return "Информация о ценах временно недоступна."
    
    def get_faq_answer(self, question: str) -> Optional[str]:
        """Ищет ответ на вопрос в FAQ"""
        try:
            question_lower = question.lower()
            faq_list = self.faq.get('frequently_asked_questions', [])
            
            for item in faq_list:
                if any(keyword in question_lower for keyword in item['question'].lower().split()[:3]):
                    return item['answer']
            
            return None
            
        except Exception as e:
            logger.error(f"Ошибка при поиске в FAQ: {e}")
            return None
    
    def get_service_details(self, service_name: str) -> Optional[str]:
        """Возвращает детальную информацию об услуге"""
        try:
            services = self.services.get('detailed_services', {})
            
            result = ""
            for key, service in services.items():
                if service_name == "all" or service_name.lower() in service['title'].lower():
                    result += f"====== {service['title']}\n\n"
                    result += f"{service['description']}\n\n"
                    result += "⚡ ВКЛЮЧАЕТ:\n"
                    for feature in service['features']:
                        result += f"• {feature}\n"
                    
                    if 'technologies' in service:
                        result += "\n🔧 ТЕХНОЛОГИИ:\n"
                        for tech in service['technologies']:
                            result += f"• {tech}\n"
                    
                    if 'supported_platforms' in service:
                        result += "\n📱 ПОДДЕРЖИВАЕМЫЕ ПЛАТФОРМЫ:\n"
                        for platform in service['supported_platforms']:
                            result += f"• {platform}\n"
                    
                    if 'supported_crm' in service:
                        result += "\n📊 ИНТЕГРАЦИЯ С CRM:\n"
                        for crm in service['supported_crm']:
                            result += f"• {crm}\n"

                    result += f"\n\n"
                    
                
            
            if result:
                result = "🛠 НАШИ УСЛУГИ::\n\n" + result
                return result
            else:
                return None
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации об услуге: {e}")
            return None
    
    def get_company_info(self) -> str:
        """Возвращает информацию о компании"""
        try:
            company = self.company_info.get('company', {})
            
            result = f"🏢 {company.get('name', 'RD-Studio')}\n\n"
            result += f"🎯 {company.get('specialization', '')}\n\n"
            
            result += "📈 НАШИ ДОСТИЖЕНИЯ:\n"
            for achievement in company.get('achievements', []):
                result += f"• {achievement}\n"
            
            result += "\n👥 НАША КОМАНДА:\n"
            team = company.get('team', {})
            for role, description in team.items():
                result += f"• {description}\n"
            
            result += "\n❤️ НАШИ ЦЕННОСТИ:\n"
            for value in company.get('values', []):
                result += f"• {value}\n"
            
            return result
            
        except Exception as e:
            logger.error(f"Ошибка при получении информации о компании: {e}")
            return "Информация о компании временно недоступна."
    
    def search_knowledge(self, query: str) -> Optional[str]:
        """Умный поиск по базе знаний"""
        query_lower = query.lower()
        
        # Поиск по ценам
        if any(keyword in query_lower for keyword in ['цена', 'стоимость', 'сколько стоит', 'прайс', 'тариф']):
            return self.get_prices_info()
        
        # Поиск по услугам
        service_keywords = {
            'лендинг': 'landing_page',
            'сайт': 'landing_page',
            'бот': 'ai_assistant',
            'ассистент': 'ai_assistant',
            'crm': 'crm_integration',
            'интеграция': 'crm_integration'
        }
        
        for keyword, service_key in service_keywords.items():
            if keyword in query_lower:
                result = self.get_service_details(service_key)
                if result:
                    return result
        
        # Поиск в FAQ
        faq_answer = self.get_faq_answer(query)
        if faq_answer:
            return faq_answer
        
        # Информация о компании
        if any(keyword in query_lower for keyword in ['компания', 'о нас', 'rd-studio', 'студи']):
            return self.get_company_info()
        
        return None

# Создаем глобальный экземпляр сервиса
knowledge_service = KnowledgeService()