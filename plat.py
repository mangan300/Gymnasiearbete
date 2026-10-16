#!/usr/bin/env python
# -*- coding: utf-8 -*-
'''
Namn: Magnus Bergkvist
Klass: Te14
Datum:

Programmet tar in bredd, tjocklek och längd på en plåt (i mm).
Användaren väljer sedan en modell för vad som händer med plåten:
    Modell 1: längden och tjockleken halveras
    Modell 2: bredden halveras
Plåten visas grafiskt före och efter bearbetningen.

Styrning:
    Klicka på en ruta och skriv in ett värde (mm)
    TAB byter ruta, ENTER kör vald modell
    "Använd resultat" gör resultatet till ny startplåt
'''

import sys
import pygame
from pygame.locals import *

BREDD_FONSTER, HOJD_FONSTER = 1280, 720

# Färger
BAKGRUND = (30, 34, 40)
PANEL = (44, 49, 58)
TEXT = (230, 233, 238)
SVAG_TEXT = (150, 156, 166)
RUTA = (60, 66, 77)
RUTA_AKTIV = (80, 120, 200)
KNAPP = (70, 77, 90)
KNAPP_VALD = (60, 140, 90)
FEL = (220, 90, 90)

# Färger för plåtens sidor (topp, front, sida)
FARG_FORE = ((170, 180, 195), (120, 130, 145), (95, 105, 120))
FARG_EFTER = ((120, 190, 230), (70, 140, 185), (55, 115, 160))


def modell_1(bredd, tjocklek, langd):
    '''Halverar längden och tjockleken.'''
    return bredd, tjocklek / 2, langd / 2


def modell_2(bredd, tjocklek, langd):
    '''Halverar bredden.'''
    return bredd / 2, tjocklek, langd


MODELLER = {
    1: ("Modell 1", "Halverar längd och tjocklek", modell_1),
    2: ("Modell 2", "Halverar bredd", modell_2),
}


class Inmatning:
    '''En textruta där man skriver in ett tal.'''

    def __init__(self, namn, x, y, varde):
        self.namn = namn
        self.rect = pygame.Rect(x, y, 200, 36)
        self.text = varde
        self.aktiv = False

    def hantera(self, event):
        if event.type == KEYDOWN and self.aktiv:
            if event.key == K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.unicode in "0123456789.," and len(self.text) < 10:
                self.text += event.unicode

    def varde(self):
        '''Returnerar talet i rutan, eller None om det inte är ett giltigt positivt tal.'''
        try:
            tal = float(self.text.replace(",", "."))
        except ValueError:
            return None
        return tal if tal > 0 else None

    def rita(self, yta, font, liten_font):
        yta.blit(liten_font.render(self.namn + " (mm)", True, SVAG_TEXT),
                 (self.rect.x, self.rect.y - 22))
        farg = RUTA_AKTIV if self.aktiv else RUTA
        pygame.draw.rect(yta, RUTA, self.rect, border_radius=6)
        pygame.draw.rect(yta, farg, self.rect, 2, border_radius=6)
        yta.blit(font.render(self.text, True, TEXT),
                 (self.rect.x + 10, self.rect.y + 6))
        if self.aktiv and pygame.time.get_ticks() // 500 % 2 == 0:
            x = self.rect.x + 12 + font.size(self.text)[0]
            pygame.draw.line(yta, TEXT, (x, self.rect.y + 8),
                             (x, self.rect.bottom - 8), 2)


class Knapp:
    def __init__(self, text, x, y, b=200, h=40):
        self.text = text
        self.rect = pygame.Rect(x, y, b, h)

    def rita(self, yta, font, vald=False):
        farg = KNAPP_VALD if vald else KNAPP
        if self.rect.collidepoint(pygame.mouse.get_pos()):
            farg = tuple(min(c + 20, 255) for c in farg)
        pygame.draw.rect(yta, farg, self.rect, border_radius=8)
        bild = font.render(self.text, True, TEXT)
        yta.blit(bild, bild.get_rect(center=self.rect.center))

    def klickad(self, event):
        return (event.type == MOUSEBUTTONDOWN and event.button == 1
                and self.rect.collidepoint(event.pos))


def iso(x, y, z, origo):
    '''Gör om en 3D-punkt till en 2D-punkt på skärmen (isometrisk vy).'''
    ox, oy = origo
    return (ox + (x - y) * 0.866, oy + (x + y) * 0.5 - z)


def rita_plat(yta, font, mitt, mm, skala, t_skala, farger, rubrik):
    '''Ritar plåten som ett 3D-block med måttangivelser.

    mm      = (bredd, tjocklek, längd) i mm
    skala   = pixlar per mm för bredd och längd
    t_skala = pixlar per mm för tjocklek (förstorad så att den syns)
    '''
    bredd, tjocklek, langd = mm
    L = langd * skala
    B = bredd * skala
    T = max(tjocklek * t_skala, 2)

    # Flytta origo så att plåten hamnar mitt på punkten "mitt"
    hornen = [iso(x, y, z, (0, 0)) for x in (0, L) for y in (0, B) for z in (0, T)]
    min_x = min(p[0] for p in hornen)
    max_x = max(p[0] for p in hornen)
    min_y = min(p[1] for p in hornen)
    max_y = max(p[1] for p in hornen)
    origo = (mitt[0] - (min_x + max_x) / 2, mitt[1] - (min_y + max_y) / 2)

    topp = [iso(0, 0, T, origo), iso(L, 0, T, origo),
            iso(L, B, T, origo), iso(0, B, T, origo)]
    front = [iso(0, B, 0, origo), iso(L, B, 0, origo),
             iso(L, B, T, origo), iso(0, B, T, origo)]
    sida = [iso(L, 0, 0, origo), iso(L, B, 0, origo),
            iso(L, B, T, origo), iso(L, 0, T, origo)]

    for yta_punkter, farg in zip((topp, front, sida), farger):
        pygame.draw.polygon(yta, farg, yta_punkter)
        pygame.draw.polygon(yta, (20, 22, 26), yta_punkter, 1)

    # Måttangivelser
    def etikett(text, pos):
        bild = font.render(text, True, TEXT)
        yta.blit(bild, bild.get_rect(center=pos))

    lx, ly = iso(L / 2, B, 0, origo)
    etikett("L = %g mm" % langd, (lx - 55, ly + 22))
    bx, by = iso(L, B / 2, 0, origo)
    etikett("B = %g mm" % bredd, (bx + 55, by + 22))
    tx, ty = iso(L, 0, T / 2, origo)
    bild = font.render("T = %g mm" % tjocklek, True, TEXT)
    yta.blit(bild, bild.get_rect(midleft=(tx + 10, ty)))

    rubrik_bild = font.render(rubrik, True, SVAG_TEXT)
    yta.blit(rubrik_bild, rubrik_bild.get_rect(center=(mitt[0], 90)))


def main():
    pygame.init()
    skarm = pygame.display.set_mode((BREDD_FONSTER, HOJD_FONSTER))
    pygame.display.set_caption("Plåtbearbetning")
    klocka = pygame.time.Clock()

    font = pygame.font.SysFont(None, 28)
    liten_font = pygame.font.SysFont(None, 22)
    stor_font = pygame.font.SysFont(None, 40)

    rutor = [Inmatning("Bredd", 40, 110, "500"),
             Inmatning("Tjocklek", 40, 190, "10"),
             Inmatning("Längd", 40, 270, "1000")]
    rutor[0].aktiv = True

    knapp_m1 = Knapp(MODELLER[1][0], 40, 340)
    knapp_m2 = Knapp(MODELLER[2][0], 40, 420)
    knapp_kor = Knapp("Kör modell", 40, 520)
    knapp_anvand = Knapp("Använd resultat", 40, 575)

    vald_modell = 1
    resultat = None
    fel = ""

    def kor():
        nonlocal resultat, fel
        varden = [r.varde() for r in rutor]
        if None in varden:
            fel = "Ange positiva tal i alla rutor"
            resultat = None
            return
        fel = ""
        resultat = (tuple(varden), MODELLER[vald_modell][2](*varden))

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            if event.type == MOUSEBUTTONDOWN and event.button == 1:
                for r in rutor:
                    r.aktiv = r.rect.collidepoint(event.pos)

            if event.type == KEYDOWN:
                if event.key == K_TAB:
                    i = next((i for i, r in enumerate(rutor) if r.aktiv), -1)
                    for r in rutor:
                        r.aktiv = False
                    rutor[(i + 1) % len(rutor)].aktiv = True
                elif event.key in (K_RETURN, K_KP_ENTER):
                    kor()
                elif event.key == K_ESCAPE:
                    pygame.quit()
                    sys.exit()

            for r in rutor:
                r.hantera(event)

            if knapp_m1.klickad(event):
                vald_modell = 1
                kor()
            if knapp_m2.klickad(event):
                vald_modell = 2
                kor()
            if knapp_kor.klickad(event):
                kor()
            if knapp_anvand.klickad(event) and resultat:
                for r, v in zip(rutor, resultat[1]):
                    r.text = "%g" % v
                kor()

        # --- Rita ---
        skarm.fill(BAKGRUND)
        pygame.draw.rect(skarm, PANEL, (0, 0, 280, HOJD_FONSTER))
        skarm.blit(stor_font.render("Plåt", True, TEXT), (40, 35))

        for r in rutor:
            r.rita(skarm, font, liten_font)

        knapp_m1.rita(skarm, font, vald_modell == 1)
        skarm.blit(liten_font.render(MODELLER[1][1], True, SVAG_TEXT), (40, 385))
        knapp_m2.rita(skarm, font, vald_modell == 2)
        skarm.blit(liten_font.render(MODELLER[2][1], True, SVAG_TEXT), (40, 465))
        knapp_kor.rita(skarm, font)
        knapp_anvand.rita(skarm, font)

        if fel:
            skarm.blit(liten_font.render(fel, True, FEL), (40, 630))

        if resultat:
            fore, efter = resultat
            # Samma skala för båda plåtarna så att man ser skillnaden.
            # Den största plåten blir ca 340 pixlar bred i bilden.
            max_lb = max(fore[0] + fore[2], efter[0] + efter[2])
            skala = 340 / (max_lb * 0.866)
            # Tjockleken förstoras så att den tjockaste plåten blir 40 px
            t_skala = 40 / max(fore[1], efter[1])

            rita_plat(skarm, font, (510, 300), fore, skala, t_skala,
                      FARG_FORE, "Före")
            rita_plat(skarm, font, (930, 300), efter, skala, t_skala,
                      FARG_EFTER, "Efter " + MODELLER[vald_modell][0].lower())

            # Tabell med värden
            y0 = 560
            kol = (340, 520, 700, 880)
            for x, t in zip(kol, ("", "Bredd", "Tjocklek", "Längd")):
                skarm.blit(font.render(t, True, SVAG_TEXT), (x, y0))
            for rad, (namn, v) in enumerate((("Före", fore), ("Efter", efter))):
                y = y0 + 34 * (rad + 1)
                skarm.blit(font.render(namn, True, TEXT), (kol[0], y))
                for x, tal in zip(kol[1:], v):
                    skarm.blit(font.render("%g mm" % tal, True, TEXT), (x, y))
            volym_text = "Volym: {:,.0f} mm³  ->  {:,.0f} mm³".format(
                fore[0] * fore[1] * fore[2], efter[0] * efter[1] * efter[2]).replace(",", " ")
            skarm.blit(liten_font.render(volym_text, True, SVAG_TEXT), (kol[0], y0 + 110))
            skarm.blit(liten_font.render("(tjockleken är förstorad i bilden)",
                                         True, SVAG_TEXT), (880, y0 + 110))
        else:
            skarm.blit(font.render("Skriv in måtten och välj en modell", True,
                                   SVAG_TEXT), (560, 340))

        pygame.display.update()
        klocka.tick(60)


if __name__ == "__main__":
    main()
