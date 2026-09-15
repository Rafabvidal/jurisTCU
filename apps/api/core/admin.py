# Register your models here.

from django.contrib import admin

from core.models.analise import Analise
from core.models.busca_salva import BuscaSalva
from core.models.orgao_julgador import OrgaoJulgador
from core.models.palavra_chave import PalavraChave
from core.models.processo import Processo

admin.site.register(Analise)
admin.site.register(BuscaSalva)
admin.site.register(OrgaoJulgador)
admin.site.register(PalavraChave)
admin.site.register(Processo)
