"""In-Memory Rate-Limiting für die teuersten/kritischsten Endpunkte.

Kontext: Alle Nutzer teilen sich einen einzigen projektweiten Gemini-API-Key
(settings.gemini_api_key) -- ein einzelnes missbräuchlich genutztes Konto (oder ein
Bug im Frontend, der z.B. den Chat in einer Schleife aufruft) kann das Kontingent für
ALLE Nutzer erschöpfen ("noisy neighbor"). Da das Backend nur als eine einzige
Render-Instanz läuft (kein verteiltes System mit mehreren Prozessen/Maschinen), reicht
slowapis Standard-In-Memory-Storage aus -- ein separater Redis-Dienst wäre hier reiner
Overhead ohne Nutzen, weil es ohnehin nur einen Prozess gibt, dessen Speicher geteilt
werden müsste.

Bekannter, bewusst akzeptierter Schwachpunkt dieses In-Memory-Ansatzes: Stürzt der
Backend-Prozess selbst ab und startet neu (z.B. durch einen Angriff oder Bug, der einen
Crash-Loop auslöst), setzt sich der Rate-Limit-Zähler bei jedem Neustart auf 0 zurück --
der Schutz würde dann faktisch nie 60 Sekunden am Stück greifen. Das wird als Randfall
zweiter Ordnung eingestuft, nicht jetzt behoben: er setzt voraus, dass ein einzelner
Nutzer den Prozess trotz der bestehenden, bereits engen 5-10/Minute-Limits überhaupt
erst zum Absturz bringen kann. Eine Behebung würde einen externen State-Store wie Redis
erfordern, der für eine einzelne Render-Free-Tier-Instanz (siehe oben) unnötiger
Overhead wäre, ohne dass ein realistischer Angriffspfad dorthin bekannt ist.
"""

from fastapi import Request
from slowapi import Limiter
from slowapi.util import get_remote_address


def _rate_limit_key(request: Request) -> str:
    """Rate-limitiert pro Nutzer-Konto (user_id aus dem verifizierten JWT), NICHT pro
    IP-Adresse: mehrere Nutzer können hinter derselben IP sitzen (z.B. Firmennetzwerk/
    NAT-Gateway), was bei einem IP-basierten Limit unbeteiligte Nutzer mitbestrafen
    würde. Umgekehrt könnte ein Angreifer ein IP-basiertes Limit leicht über mehrere
    IPs umgehen, während ein Konto knapper ist.

    request.state.user_id wird von app.auth.get_current_user_id gesetzt, welches als
    FastAPI-Dependency IMMER vor dem eigentlichen Endpunkt (und damit vor dieser
    Key-Funktion) ausgeführt wird -- ein zweites JWT-Decoding hier ist daher unnötig.
    Der Fallback auf die IP-Adresse greift nur in Ausnahmefällen, in denen die
    Auth-Dependency in Tests via dependency_overrides ersetzt wurde (dort läuft die
    echte get_current_user_id nie und request.state.user_id bleibt ungesetzt) oder ein
    zukünftiger, nicht-authentifizierter Endpunkt versehentlich rate-limitiert würde --
    er verhindert, dass die Rate-Limit-Prüfung selbst mit einem Fehler abbricht.
    """
    user_id = getattr(request.state, "user_id", None)
    if user_id:
        return str(user_id)
    return get_remote_address(request)


# key_style="endpoint" statt des slowapi-Defaults "url": unsere Routen enthalten
# notebook_id als Pfad-Segment (z.B. /notebooks/{notebook_id}/chat). Mit dem
# URL-basierten Default würde jede notebook_id einen EIGENEN Rate-Limit-Bucket
# bekommen -- ein Nutzer könnte das Limit dann einfach umgehen, indem er auf mehrere
# Notebooks verteilt anfragt. "endpoint" bindet den Bucket stattdessen an die
# Endpunkt-Funktion selbst, unabhängig davon, für welches Notebook sie aufgerufen wird.
limiter = Limiter(key_func=_rate_limit_key, key_style="endpoint")
