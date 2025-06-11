"""
SimplePDFPlugin - плагин для генерации PDF документов
Основан на коде с Azure Aluminum сервера (onto_mikro_v2)
"""

import tempfile
import os
import traceback
import markdown
from typing import Dict, Any, Optional
from loguru import logger

from app.core.base_plugin import BasePlugin


class SimplePDFPlugin(BasePlugin):
    """Простой плагин для генерации PDF документов"""
    
    def __init__(self):
        super().__init__("simple_pdf")
        self.logo_path = None
        
    async def _do_initialize(self):
        """Инициализация плагина"""
        try:
            # Путь к логотипу
            self.logo_path = os.path.join(os.getcwd(), "assets", "logos", "onto_logo.png")
            
            if os.path.exists(self.logo_path):
                logger.info(f"✅ PDF плагин инициализирован с логотипом: {self.logo_path}")
            else:
                logger.warning(f"⚠️ Логотип не найден: {self.logo_path}")
                self.logo_path = None
                
            # Проверяем наличие pdfkit
            try:
                import pdfkit
                logger.info("✅ pdfkit доступен для генерации PDF")
            except ImportError:
                logger.error("❌ pdfkit не установлен! Установите: pip install pdfkit")
                raise
                
        except Exception as e:
            logger.error(f"❌ Ошибка инициализации PDF плагина: {e}")
            raise
    
    def register_handlers(self) -> Dict[str, Any]:
        """Регистрация обработчиков шагов"""
        return {
            "pdf_generate": self._handle_generate_pdf,
            "pdf_generate_from_text": self._handle_generate_from_text,
        }
    
    async def healthcheck(self) -> bool:
        """Проверка здоровья плагина"""
        try:
            import pdfkit
            return True
        except ImportError:
            return False
    
    async def _handle_generate_pdf(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Обработчик генерации PDF"""
        params = step_data.get("params", {})
        
        try:
            content = self._resolve_value(params.get("content", ""), context)
            title = self._resolve_value(params.get("title", "Документ"), context)
            output_var = params.get("output_var", "pdf_result")
            use_logo = params.get("use_logo", True)
            
            if not content:
                context[output_var] = {"success": False, "error": "Не указан контент для PDF"}
                return
            
            # Генерируем PDF
            logo_path = self.logo_path if use_logo else None
            pdf_path = self._generate_pdf_from_text(content, title, logo_path)
            
            if pdf_path:
                context[output_var] = {
                    "success": True,
                    "pdf_path": pdf_path,
                    "title": title,
                    "file_size": os.path.getsize(pdf_path) if os.path.exists(pdf_path) else 0
                }
                logger.info(f"✅ PDF сгенерирован: {pdf_path}")
            else:
                context[output_var] = {"success": False, "error": "Ошибка генерации PDF"}
                logger.error("❌ Не удалось сгенерировать PDF")
                
        except Exception as e:
            logger.error(f"❌ Ошибка генерации PDF: {e}")
            context["__step_error__"] = f"PDF генерация: {str(e)}"
    
    async def _handle_generate_from_text(self, step_data: Dict[str, Any], context: Dict[str, Any]) -> None:
        """Упрощенный обработчик генерации PDF из текста"""
        await self._handle_generate_pdf(step_data, context)
    
    def _generate_pdf_from_text(self, text: str, title: str = "Документ", logo_path: Optional[str] = None) -> Optional[str]:
        """
        Генерирует PDF из текста с поддержкой Markdown и логотипа через pdfkit (HTML → PDF).
        Возвращает путь к PDF или None при ошибке.
        
        Основано на коде с Azure Aluminum сервера.
        """
        try:
            logger.info(f"🔧 Генерация PDF: title='{title}', text_length={len(text)}")
            
            # Преобразуем Markdown в HTML
            try:
                text_html = markdown.markdown(text or '', extensions=['extra', 'smarty'])
            except Exception as e:
                logger.error(f"❌ Ошибка при преобразовании Markdown: {e}")
                text_html = text or ''
            
            # Абсолютный путь к логотипу через file://
            logo_html = ''
            if logo_path and os.path.exists(logo_path):
                abs_logo = os.path.abspath(logo_path)
                logo_html = f'<img src="file://{abs_logo}" class="logo" alt="Логотип" />'
                logger.info(f"📷 Используется логотип: {abs_logo}")
            else:
                logger.warning("⚠️ Логотип не используется")
            
            # Формируем HTML с премиальным стилем (из Azure Aluminum)
            html = f"""
            <html>
            <head>
                <meta charset='utf-8'>
                <title>{title}</title>
                <style>
                    body {{
                        font-family: 'PT Serif', Georgia, serif;
                        font-size: 17pt;
                        color: #222;
                        line-height: 1.5;
                        margin: 20mm 15mm 20mm 15mm;
                    }}
                    h1, h2, h3, h4 {{
                        font-family: 'PT Sans', Arial, sans-serif;
                        font-weight: bold;
                        color: #4e54c8;
                        margin-top: 1.5em;
                        margin-bottom: 0.5em;
                    }}
                    h1 {{ font-size: 26pt; }}
                    h2 {{ font-size: 22pt; }}
                    h3 {{ font-size: 19pt; }}
                    h4 {{ font-size: 17pt; color: #333; }}
                    pre, code {{
                        font-family: 'PT Mono', 'DejaVu Sans Mono', monospace;
                        font-size: 15pt;
                        background: #f8f8f8;
                        padding: 0.5em;
                        border-radius: 4px;
                    }}
                    b, strong {{ color: #111; }}
                    hr {{ border: none; border-top: 1px solid #eee; margin: 2em 0; }}
                    .logo {{ display: block; margin: 0 auto 24px auto; max-width: 220px; }}
                    .section {{ margin-bottom: 2em; }}
                </style>
            </head>
            <body>
                {logo_html}
                <div class="section">
                    {text_html}
                </div>
            </body>
            </html>
            """
            
            logger.info(f"📄 HTML сформирован, длина: {len(html)} символов")
            
            # Создаем временный файл для PDF
            with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
                try:
                    import pdfkit
                    logger.info("🔧 Генерация PDF через pdfkit...")
                    
                    pdfkit.from_string(html, tmp.name, options={
                        'encoding': 'utf-8',
                        'quiet': '',
                        'page-size': 'A4',
                        'margin-top': '20mm',
                        'margin-bottom': '20mm',
                        'margin-left': '15mm',
                        'margin-right': '15mm',
                        'disable-smart-shrinking': '',
                        'enable-local-file-access': '',
                    })
                    
                    logger.info(f"✅ PDF успешно сгенерирован: {tmp.name}")
                    return tmp.name
                    
                except Exception as e:
                    logger.error(f"❌ Ошибка генерации PDF через pdfkit: {e}")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ Критическая ошибка генерации PDF: {e}")
            return None
    
    def _resolve_value(self, value: Any, context: Dict[str, Any]) -> Any:
        """Простая подстановка значений из контекста"""
        if isinstance(value, str) and "{" in value and "}" in value:
            try:
                return value.format(**context)
            except (KeyError, ValueError) as e:
                logger.warning(f"Не удалось разрешить '{value}': {e}")
                return value
        return value 