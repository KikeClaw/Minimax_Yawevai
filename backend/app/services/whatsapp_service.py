"""
WhatsApp Bulk Messaging Service for YAWEB.AI
Send personalized WhatsApp messages to multiple prospects with rate limiting.
"""

from typing import List, Dict, Optional
from pydantic import BaseModel
from datetime import datetime, timedelta
import time
import os

# ============================================================================
# Configuration
# ============================================================================

TWILIO_ACCOUNT_SID = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_AUTH_TOKEN = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WHATSAPP_NUMBER = os.getenv("TWILIO_WHATSAPP_NUMBER", "+14155238886")

# Rate limiting configuration
MAX_MESSAGES_PER_HOUR = 50
MESSAGE_INTERVAL_SECONDS = 3600 / MAX_MESSAGES_PER_HOUR  # 72 seconds between messages

# Default price template variable
PRECIO_DEFAULT = "149"

# ============================================================================
# Message Templates (Spanish)
# ============================================================================

HOLA_TEMPLATE = """Hola {nombre}! Hemos creado una web demo gratis para tu negocio {negocio}:

👉 demo.yawweb.ai/{slug}

Sin compromiso, es solo para que veas cómo podría quedar tu web profesional.

¿Te gusta? Si quieres activarla, solo {precio}/año.
"""

SEGUIMIENTO_TEMPLATE = """Hola {nombre}! Te escribo porque hace unos días te preparé una web demo para {negocio}:

👉 demo.yawweb.ai/{slug}

¿Te has podido mirar lo que preparé? Si te gusta la idea, podemos activarla hoy por solo {precio}/año.
"""

# Template registry
TEMPLATES = {
    "hola": HOLA_TEMPLATE,
    "seguimiento": SEGUIMIENTO_TEMPLATE,
}

# ============================================================================
# Data Models
# ============================================================================

class Prospect(BaseModel):
    """Prospect data model for WhatsApp messaging."""
    phone: str
    nombre: str
    negocio: str
    slug: str
    precio: Optional[str] = PRECIO_DEFAULT


class MessageResult(BaseModel):
    """Result of sending a single message."""
    phone: str
    success: bool
    message_id: Optional[str] = None
    error: Optional[str] = None
    sent_at: Optional[datetime] = None


class BatchResult(BaseModel):
    """Result of a batch send operation."""
    total: int
    sent: int
    failed: int
    results: List[MessageResult]
    duration_seconds: float
    started_at: datetime
    completed_at: Optional[datetime] = None


# ============================================================================
# Rate Limiter
# ============================================================================

class RateLimiter:
    """
    Rate limiter to prevent WhatsApp API bans.
    Enforces maximum messages per hour with precise timing.
    """

    def __init__(self, max_per_hour: int = MAX_MESSAGES_PER_HOUR):
        self.max_per_hour = max_per_hour
        self.interval_seconds = 3600 / max_per_hour
        self.last_sent_time: Optional[float] = None
        self.sent_count = 0
        self.window_start: Optional[float] = None

    def can_send(self) -> bool:
        """Check if a message can be sent now."""
        current_time = time.time()

        # Reset counter if window has passed (1 hour)
        if self.window_start and current_time - self.window_start >= 3600:
            self.sent_count = 0
            self.window_start = current_time

        # Initialize window if needed
        if self.window_start is None:
            self.window_start = current_time

        return self.sent_count < self.max_per_hour

    def wait_if_needed(self) -> None:
        """Wait if necessary to respect rate limits."""
        current_time = time.time()

        # Check if we need to wait for the next window
        if self.sent_count >= self.max_per_hour:
            if self.window_start:
                wait_time = 3600 - (current_time - self.window_start)
                if wait_time > 0:
                    time.sleep(wait_time)
            # Reset for new window
            self.sent_count = 0
            self.window_start = current_time

        # Enforce minimum interval between messages
        if self.last_sent_time:
            elapsed = current_time - self.last_sent_time
            if elapsed < self.interval_seconds:
                time.sleep(self.interval_seconds - elapsed)

        self.last_sent_time = time.time()
        self.sent_count += 1

    def reset(self) -> None:
        """Reset the rate limiter state."""
        self.last_sent_time = None
        self.sent_count = 0
        self.window_start = None


# ============================================================================
# Twilio Client (Mock for testing)
# ============================================================================

class TwilioClient:
    """
    Twilio WhatsApp client wrapper.
    Falls back to mock mode when credentials are not configured.
    """

    def __init__(self, account_sid: Optional[str], auth_token: Optional[str],
                 from_number: str, mock_mode: bool = False):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.from_number = from_number
        self.mock_mode = mock_mode or not all([account_sid, auth_token])

        if self.mock_mode:
            print("[WhatsApp Mock Mode] Twilio credentials not configured. Messages will be printed instead of sent.")
        else:
            from twilio.rest import Client
            self.client = Client(account_sid, auth_token)

    def send_message(self, to: str, body: str) -> Dict:
        """
        Send a WhatsApp message.

        Args:
            to: Recipient phone number (format: whatsapp:+1234567890)
            body: Message body text

        Returns:
            Dict with message_id on success or error information
        """
        if self.mock_mode:
            print(f"\n[MOCK] Sending WhatsApp message:")
            print(f"  From: {self.from_number}")
            print(f"  To: {to}")
            print(f"  Message: {body[:100]}{'...' if len(body) > 100 else ''}")
            return {"sid": f"MOCK_{int(time.time())}", "status": "sent"}

        try:
            message = self.client.messages.create(
                body=body,
                from_=self.from_number,
                to=to
            )
            return {"sid": message.sid, "status": str(message.status)}
        except Exception as e:
            return {"error": str(e), "status": "failed"}


# ============================================================================
# WhatsApp Service
# ============================================================================

class WhatsAppService:
    """
    Main service for sending bulk WhatsApp messages with personalization
    and rate limiting to avoid WhatsApp bans.
    """

    def __init__(self):
        """Initialize the WhatsApp service with Twilio client and rate limiter."""
        self.rate_limiter = RateLimiter()
        self.twilio_client = TwilioClient(
            account_sid=TWILIO_ACCOUNT_SID,
            auth_token=TWILIO_AUTH_TOKEN,
            from_number=f"whatsapp:{TWILIO_WHATSAPP_NUMBER}",
            mock_mode=False  # Will auto-detect based on credentials
        )

    def generate_message(self, prospect: Prospect, template_name: str) -> str:
        """
        Generate a personalized message from a template.

        Args:
            prospect: Prospect object with template variables
            template_name: Name of the template to use ('hola' or 'seguimiento')

        Returns:
            Personalized message string with all variables replaced

        Raises:
            ValueError: If template_name is not found
        """
        if template_name not in TEMPLATES:
            available = ", ".join(TEMPLATES.keys())
            raise ValueError(f"Template '{template_name}' not found. Available: {available}")

        template = TEMPLATES[template_name]

        # Replace all template variables
        message = template.format(
            nombre=prospect.nombre,
            negocio=prospect.nombre,
            slug=prospect.slug,
            precio=prospect.precio if hasattr(prospect, 'precio') and prospect.precio else PRECIO_DEFAULT
        )

        return message

    def send_message(self, phone: str, message: str, prospect: Optional[Prospect] = None) -> MessageResult:
        """
        Send a single WhatsApp message with rate limiting.

        Args:
            phone: Recipient phone number
            message: Message body to send
            prospect: Optional prospect data for logging

        Returns:
            MessageResult with status information
        """
        # Normalize phone number format
        normalized_phone = self._normalize_phone(phone)

        # Apply rate limiting
        self.rate_limiter.wait_if_needed()

        # Send message via Twilio
        to_address = f"whatsapp:{normalized_phone}"
        result = self.twilio_client.send_message(to_address, message)

        # Build response
        if "error" in result:
            return MessageResult(
                phone=normalized_phone,
                success=False,
                error=result["error"],
                sent_at=datetime.now()
            )
        else:
            return MessageResult(
                phone=normalized_phone,
                success=True,
                message_id=result.get("sid"),
                sent_at=datetime.now()
            )

    def send_batch(self, prospects: List[Prospect], template_name: str = "hola",
                   progress_callback: Optional[callable] = None) -> BatchResult:
        """
        Send bulk WhatsApp messages to multiple prospects with rate limiting.

        Args:
            prospects: List of Prospect objects to send messages to
            template_name: Template to use for personalization
            progress_callback: Optional callback function called after each message

        Returns:
            BatchResult with overall statistics and individual message results
        """
        start_time = time.time()
        start_datetime = datetime.now()
        results: List[MessageResult] = []

        print(f"\n[WhatsApp Batch] Starting to send {len(prospects)} messages using '{template_name}' template")

        for i, prospect in enumerate(prospects, 1):
            print(f"[{i}/{len(prospects)}] Processing {prospect.nombre} ({prospect.telefono})...")

            # Generate personalized message
            try:
                message = self.generate_message(prospect, template_name)
            except ValueError as e:
                print(f"  [ERROR] {e}")
                results.append(MessageResult(
                    phone=prospect.telefono,
                    success=False,
                    error=str(e),
                    sent_at=datetime.now()
                ))
                continue

            # Send the message
            result = self.send_message(prospect.telefono, message, prospect)
            results.append(result)

            if result.success:
                print(f"  [OK] Message sent successfully")
            else:
                print(f"  [FAILED] {result.error}")

            # Progress callback
            if progress_callback:
                progress_callback(i, len(prospects), result)

            # Small delay to avoid overwhelming the API
            time.sleep(0.5)

        end_time = time.time()
        duration = end_time - start_time

        # Calculate statistics
        sent_count = sum(1 for r in results if r.success)
        failed_count = sum(1 for r in results if not r.success)

        batch_result = BatchResult(
            total=len(prospects),
            sent=sent_count,
            failed=failed_count,
            results=results,
            duration_seconds=duration,
            started_at=start_datetime,
            completed_at=datetime.now()
        )

        print(f"\n[WhatsApp Batch] Completed!")
        print(f"  Total: {batch_result.total}")
        print(f"  Sent: {batch_result.sent}")
        print(f"  Failed: {batch_result.failed}")
        print(f"  Duration: {batch_result.duration_seconds:.2f} seconds")

        return batch_result

    def _normalize_phone(self, phone: str) -> str:
        """
        Normalize phone number to international format.
        Handles various input formats (with/without +, spaces, dashes, etc.)
        """
        # Remove all non-digit characters except leading +
        digits = ''.join(c for c in phone if c.isdigit() or c == '+')

        # Ensure it starts with +
        if not digits.startswith('+'):
            digits = '+' + digits

        # Assume Spanish phone numbers if no country code
        if digits.count('+') == 1 and len(digits.split('+')[1]) <= 10:
            # Looks like a Spanish number without country code
            if not digits.startswith('+34'):
                digits = '+34' + digits.lstrip('+')

        return digits

    def get_rate_limit_status(self) -> Dict:
        """Get current rate limiter status."""
        return {
            "sent_count": self.rate_limiter.sent_count,
            "max_per_hour": self.rate_limiter.max_per_hour,
            "interval_seconds": self.rate_limiter.interval_seconds,
            "last_sent_time": self.rate_limiter.last_sent_time
        }


# ============================================================================
# Convenience Functions
# ============================================================================

def create_prospect(phone: str, nombre: str, negocio: str, slug: str,
                    precio: Optional[str] = None) -> Prospect:
    """Helper function to create a Prospect object."""
    return Prospect(
        phone=phone,
        nombre=nombre,
        negocio=negocio,
        slug=slug,
        precio=precio
    )


def send_single_message(phone: str, template_name: str, prospect_data: Dict) -> MessageResult:
    """
    Convenience function to send a single message.

    Args:
        phone: Recipient phone number
        template_name: Template to use ('hola' or 'seguimiento')
        prospect_data: Dict with keys: nombre, negocio, slug, precio (optional)

    Returns:
        MessageResult with sending status
    """
    service = WhatsAppService()
    prospect = Prospect(
        phone=phone,
        nombre=prospect_data.get("nombre", "Cliente"),
        negocio=prospect_data.get("negocio", "negocio"),
        slug=prospect_data.get("slug", "demo"),
        precio=prospect_data.get("precio")
    )
    message = service.generate_message(prospect, template_name)
    return service.send_message(phone, message)


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    # Example: Send test messages
    print("WhatsApp Service initialized")
    print(f"Mock Mode: {'Yes' if not TWILIO_ACCOUNT_SID else 'No'}")

    # Create test prospects
    test_prospects = [
        create_prospect(
            phone="+34612345678",
            nombre="Carlos",
            negocio="Restaurante El Galeon",
            slug="restaurante-el-galeon",
            precio="149"
        ),
        create_prospect(
            phone="+34687654321",
            nombre="Maria",
            negocio="Consultoria Legal",
            slug="consultoria-maria",
            precio="199"
        ),
    ]

    # Example: Generate a message
    if test_prospects:
        sample = test_prospects[0]
        print(f"\nGenerated message for {sample.nombre}:")
        print("-" * 50)
        service = WhatsAppService()
        msg = service.generate_message(sample, "hola")
        print(msg)

    print("\nTo send batch messages, use:")
    print("  service = WhatsAppService()")
    print("  results = service.send_batch(prospects, 'hola')")