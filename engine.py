import mido


class CounterpointEngine:
    # Usamos un diccionario de clase para mapear notas a su valor de pitch class (0-11)
    PITCH_CLASSES = {'C': 0, 'C#': 1, 'D': 2, 'D#': 3, 'E': 4, 'F': 5,
                     'F#': 6, 'G': 7, 'G#': 8, 'A': 9, 'A#': 10, 'B': 11}

    def __init__(self, midi_file_path=None, tonic_name="C"):
        self.midi_file_path = midi_file_path
        self.tonic_name = tonic_name.upper()
        # Convertimos la letra (ej. "C") a su clase matematica (0)
        self.tonic_pitch_class = self.PITCH_CLASSES.get(self.tonic_name, 0)
        self.melody_notes = []
        self.note_durations = []
        self.ticks_per_beat = 0
        self.whole_note_ticks = 0

    def load_midi(self):
        """Se extraen los mensajes note_on y sus duraciones del archivo MIDI."""
        if not self.midi_file_path:
            print("No se proporcionó archivo MIDI.")
            return False

        print(f"Cargando {self.midi_file_path}...")

        try:
            mid = mido.MidiFile(self.midi_file_path)

            # Calculamos la duracion exacta de una redonda (4 tiempos) segun la resolucion
            self.ticks_per_beat = mid.ticks_per_beat
            self.whole_note_ticks = self.ticks_per_beat * 4

            for track in mid.tracks:
                for msg in track:
                    # Capturamos el inicio de la nota
                    if msg.type == 'note_on' and msg.velocity > 0:
                        self.melody_notes.append(msg.note)

                    # Capturamos el final de la nota (note_off o note_on con velocity 0)
                    elif msg.type == 'note_off' or (msg.type == 'note_on' and msg.velocity == 0):
                        if msg.time > 0:
                            self.note_durations.append(msg.time)

            # mensaje limpio para el usuario
            print(f"Éxito: Archivo analizado. Se detectó una melodía de {len(self.melody_notes)} notas.")
            return True

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.midi_file_path}. Revisa que esté en la misma carpeta.")
            return False
    def _check_valid_start_end(self):
        """Reglas estructurales: Inicio y fin correctos del Cantus Firmus."""
        first_note = self.melody_notes[0]
        last_note = self.melody_notes[-1]

        if (first_note % 12) != self.tonic_pitch_class:
            print(f"Error estructural: La melodía empieza en {first_note}, que no es la tónica {self.tonic_name}.")
            return False

        if (last_note % 12) != self.tonic_pitch_class:
            print(f"Error estructural: La melodía termina en {last_note}, que no es la tónica {self.tonic_name}.")
            return False

        print(f"Regla aprobada: El Cantus firmus empieza y termina en la tónica {self.tonic_name}.")
        return True

    def _check_structure_and_range(self):
        """Reglas 1, 3 y 4: Extensión, ámbito y tesitura vocal (con warnings)."""
        total_notes = len(self.melody_notes)
        if total_notes < 8 or total_notes > 16:
            print(f"Error estructural: El Cantus firmus pedagógico tiene {total_notes} notas. Debe tener entre 8 y 16.")
            return False

        highest_note = max(self.melody_notes)
        lowest_note = min(self.melody_notes)
        ambitus = highest_note - lowest_note

        # Advertencias de estilo para el rango
        if ambitus > 16:
            print(
                f"Sugerencia de ámbito: Rango de {ambitus} semitonos (mayor a una décima). Se sugiere reducirlo para asegurar una mejor cantabilidad.")
        elif ambitus > 12:
            print(
                f"Nota de ambito: Rango de {ambitus} semitonos. Es valido pero el ideal pedagógico es no superar la octava (12 semitonos).")

        # Advertencias de estilo para el registro
        if lowest_note < 40 or highest_note > 81:
            print(
                f"Sugerencia de registro: Melodía en tesitura poco cantable ({lowest_note} a {highest_note}). Se sugiere mantener en un rango vocal cómodo.")

        print("Regla estructural aprobada. Evaluaciones de ámbito y tesitura completadas.")
        return True

    def _check_rhythm(self):
        """Regla 2: Tipo de figura (Sólo redondas con margen de tolerancia)."""

        # Margen de tolerancia del 5% para compensar exportaciones de DAWs como MuseScore
        # o interpretaciones humanas si el usuario toca con metronomo.
        tolerance = self.whole_note_ticks * 0.05
        lower_bound = self.whole_note_ticks - tolerance
        upper_bound = self.whole_note_ticks + tolerance

        for i, duration in enumerate(self.note_durations):
            if not (lower_bound <= duration <= upper_bound):
                print(f"Error rítmico en la nota {i+1}: Figura incorrecta: Recuerda que en la primera especie se usan exclusivamente redondas.")
                return False

        print("Regla rítmica: Toda la melodía está escrita en redondas.")
        return True

    def _check_climax(self):
        """Reglas 7, 8, 9 y 10: Análisis del clímax melódico."""
        climax_note = max(self.melody_notes)
        climax_count = self.melody_notes.count(climax_note)
        total_notes = len(self.melody_notes)
        climax_index = self.melody_notes.index(climax_note)

        # Reglas 7 y 9: Climax unico y prohibicion de climax repetido
        if climax_count > 1:
            print(
                f"Error de clímax: La nota más alta ({climax_note}) se repite {climax_count} veces. El clímax debe ser único.")
            return False

        # Regla 8: Ubicacion del climax (No en extremos)
        if climax_index == 0 or climax_index == total_notes - 1:
            print("Error de clímax: El clímax no puede estar en el primer, ni en el último compás.")
            return False

        # Regla 8 (Advertencia pedagogica): Preferentemente en el segundo tercio del ejercicio
        tercio_inicio = total_notes // 3
        tercio_fin = (total_notes * 2) // 3
        if not (tercio_inicio <= climax_index <= tercio_fin):
            print(
                f"Sugerencia de clímax: El clímax está en el compás {climax_index + 1}. Pedagógicamentea - en nivel básico - se sugiere ubicarlo en el segundo tercio del ejercicio.")

        # Regla 10: Climax nunca en la sensible (7mo grado)
        # Se calcula la sensible sumando 11 semitonos a la tonica
        sensible_pitch_class = (self.tonic_pitch_class + 11) % 12
        if (climax_note % 12) == sensible_pitch_class:
            print(
                f"Error de clímax: La nota clímax ({climax_note}) es la sensible ({self.tonic_name} mayor). Esto genera una tensión acústica excesiva y poco estética.")
            return False

        print("Reglas de clímax aprobadas: Único, bien ubicado y sin tensión de sensible.")
        return True

    def _check_valid_intervals(self) -> bool:
        """Reglas de movimiento: Saltos permitidos y prohibidos."""
        # 6=tritono, 10=septima menor, 11=septima mayor (El 0 se evalua en notas repetidas)
        forbidden_intervals = [6, 10, 11]

        for i in range(len(self.melody_notes) - 1):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]
            interval = abs(current_note - next_note)

            if interval > 12:
                print(f"Error de movimiento: Salto mayor a una octava entre {current_note} y {next_note} ({interval} semitonos).")
                return False

            if interval in forbidden_intervals:
                print(f"Error de movimiento: Intervalo prohibido de {interval} semitonos entre {current_note} y {next_note}.")
                return False

        print("Regla de saltos: Todos los intervalos son válidos.")
        return True

    def _check_repeated_notes(self) -> bool:
        """Regla 14: Prohibición de notas repetidas (unísono)."""
        for i in range(len(self.melody_notes) - 1):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]

            if current_note == next_note:
                print(
                    f"Error de movimiento: Nota repetida detectada ({current_note} -> {next_note}). Está estrictamente prohibido repetir la misma nota en el Cantus Firmus.")
                return False

        print("Regla de conduccion: No hay notas repetidas consecutivamente.")
        return True

    def _check_stepwise_motion(self) -> bool:
        """Regla 11: Predominio de grados conjuntos (Movimiento por segundas)."""
        if len(self.melody_notes) < 2:
            return False

        stepwise_count = 0
        total_movements = len(self.melody_notes) - 1

        for i in range(total_movements):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]
            interval = abs(current_note - next_note)

            # grados conjuntos son 1 (2da menor) o 2 (2da mayor) semitonos
            if interval == 1 or interval == 2:
                stepwise_count += 1

            # nota para el dev: el unisono (0) se evaluara como prohibido en las reglas de saltos

        stepwise_percentage = (stepwise_count / total_movements) * 100

        # Warning pedagogico en lugar de un error estricto
        if stepwise_percentage <= 50:
            print(
                f"Advertencia de conducción: Sólo el {stepwise_percentage:.1f}% de los movimientos son por grado conjunto. Se recomienda usar más pasos de segunda para mayor fluidez vocal.")
        else:
            print(f"Regla de conducción: Buen predominio de grados conjuntos ({stepwise_percentage:.1f}%).")

        # Siempre retorna true para no detener el analisis por cuestiones de estilo/estetica
        return True

    def _check_undulating_curve(self) -> bool:
        """Reglas 12 y 13: Curva ondulante y variedad direccional."""
        if len(self.melody_notes) < 3:
            return True

        consecutive_direction = 0
        current_direction = 0  # 1 para subir, -1 para bajar
        warning_triggered = False  # Bandera para saber si se lanza la advertencia

        for i in range(len(self.melody_notes) - 1):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]

            if next_note > current_note:
                direction = 1
            elif next_note < current_note:
                direction = -1
            else:
                direction = 0  # unisono

            if direction == current_direction and direction != 0:
                consecutive_direction += 1
            else:
                consecutive_direction = 1
                current_direction = direction

            # 5 movimientos seguidos = 6 notas en la misma dirección (ERROR)
            if consecutive_direction == 5:
                print(
                    f"Error de conducción: Se detectó un movimiento que se mueve en la misma dirección durante 6 notas.")
                return False

            # 4 movimientos seguidos = 5 notas en la misma dirección (WARNING)
            elif consecutive_direction == 4:
                print(
                    f"Advertencia: Se detectó un movimiento que lleva 5 notas en la misma dirección. Se recomienda alternar para mantener una curva satisfactoria.")
                warning_triggered = True
                # No se retorna aqui para que el ciclo siga vigilando si llega a la 6ta nota

        # Si termino toda la pieza y nunca entro al warning
        if not warning_triggered:
            print("Regla de conducción: La melodía tiene una curva ondulante con buena variedad direccional.")

        return True
    def _check_futile_oscillation(self) -> bool:
        """Regla 15: Advertencia para oscilación fútil (rebotes tipo A-B-A)."""
        if len(self.melody_notes) < 3:
            return True

        for i in range(len(self.melody_notes) - 2):
            # Se compara la nota actual con la que esta dos posiciones adelante
            if self.melody_notes[i] == self.melody_notes[i + 2]:
                print(
                    f"Advertencia: Sugerencia de conducción. Oscilación detectada ({self.melody_notes[i]} -> {self.melody_notes[i + 1]} -> {self.melody_notes[i + 2]}). Trata de evitar rebotes inmediatos para no estancar la fluidez de la línea.")
                return True

        print("Regla de conducción: No hay oscilaciones fútiles (rebotes A-B-A).")
        return True

    def _check_sequences(self) -> bool:
        """Regla 16: Evitar diseños rítmico-melódicos idénticos que se repitan a diferentes alturas."""
        if len(self.melody_notes) < 6:
            return True

        # Se extrae un arreglo de intervalos relativos
        intervals = []
        for i in range(len(self.melody_notes) - 1):
            intervals.append(self.melody_notes[i + 1] - self.melody_notes[i])

        # Se busca si un patron de 2 intervalos (un motivo de 3 notas) se repite
        pattern_length = 2
        for i in range(len(intervals) - pattern_length):
            pattern = intervals[i:i + pattern_length]

            # Se compara ese patron con el resto de la melodia hacia adelante
            for j in range(i + pattern_length, len(intervals) - pattern_length + 1):
                if intervals[j:j + pattern_length] == pattern:
                    print(
                        f"Advertencia: Secuencias similares melódicas detectadas. Un motivo de 3 o más notas se repite de forma mecánica. Pedagógicamente se prefiere la asimetría.")
                    return True  # Es advertencia estetica, no se rompe la ejecucion

        print("Regla de conducción: No se detectaron secuencias mecánicas similares.")
        return True

    def check_cantus_firmus_rules(self) -> bool:
        """Director de orquesta: Evalúa todas las reglas paso a paso."""
        if not self.melody_notes:
            print("No hay notas cargadas para evaluar.")
            return False

        print("\n--- Evaluando reglas de Cantus Firmus ---")

        if not self._check_valid_start_end(): return False
        if not self._check_structure_and_range(): return False
        if not self._check_rhythm(): return False
        if not self._check_climax(): return False
        if not self._check_valid_intervals(): return False
        if not self._check_repeated_notes(): return False
        if not self._check_stepwise_motion(): return False
        if not self._check_undulating_curve(): return False
        if not self._check_futile_oscillation(): return False
        if not self._check_sequences(): return False

        print("\nEl Cantus Firmus ha pasado todas las pruebas estructurales y de movimiento.")
        return True


if __name__ == "__main__":
    engine = CounterpointEngine("cantus_test.mid", tonic_name="C")
    if engine.load_midi():
        engine.check_cantus_firmus_rules()