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

            # Calculamos la duracion exacta de una redonda (4 tiempos)
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
            print(f"Archivo .mid analizado. Se detectó un ejercicio de {len(self.melody_notes)} notas.")
            return True

        except FileNotFoundError:
            print(f"Error: No se encontró el archivo {self.midi_file_path}. Revisa que esté en la misma carpeta.")
            return False

    @staticmethod
    def _midi_to_name(midi_note: int) -> str:
        """Traductor: Convierte un numero MIDI (ej. 60) a nombre de nota (ej. Do4)."""
        notas = ['Do', 'Do#', 'Re', 'Re#', 'Mi', 'Fa', 'Fa#', 'Sol', 'Sol#', 'La', 'La#', 'Si']
        nombre_nota = notas[midi_note % 12]

        # En el estandar MIDI, el Do central es el 60 (Do4).
        # Dividimos entre 12 y restamos 1 para sacar el numero de octava correcto.
        octava = (midi_note // 12) - 1

        return f"{nombre_nota}{octava}"

    def _check_valid_start_end(self):
        """Regla de inicio y fin en tónica."""
        first_note = self.melody_notes[0]
        last_note = self.melody_notes[-1]

        if (first_note % 12) != self.tonic_pitch_class:
            print(f"Error: La melodía empieza en {first_note}, que no es la tónica {self.tonic_name}.")
            return False

        if (last_note % 12) != self.tonic_pitch_class:
            print(f"Error: La melodía termina en {last_note}, que no es la tónica {self.tonic_name}.")
            return False

        print(f"Correcto: El Cantus firmus empieza y termina en la tónica {self.tonic_name}.")
        return True

    def _check_structure_and_range(self):
        """Regla de control de la longitud y tesitura vocal (con advertencias)."""
        total_notes = len(self.melody_notes)
        if total_notes < 8 or total_notes > 16:
            print(f"Error: El Cantus firmus tiene {total_notes} notas. Debe tener entre 8 y 16.")
            return False

        highest_note = max(self.melody_notes)
        lowest_note = min(self.melody_notes)
        ambitus = highest_note - lowest_note

        # Advertencias para el rango
        if ambitus > 16:
            print(
                f"Sugerencia: Rango de {ambitus} semitonos (mayor a una décima). Se sugiere reducirlo para asegurar una mejor cantabilidad.")
        elif ambitus > 12:
            print(
                f"Sugerencia: Rango de {ambitus} semitonos. Es válido pero el ideal pedagógico es no superar la octava (12 semitonos).")

        # Advertencias para el registro
        if lowest_note < 40 or highest_note > 81:
            print(
                f"Sugerencia: Melodía en tesitura poco cantable ({lowest_note} a {highest_note}). Se sugiere mantener un rango vocal cómodo.")

        print("Correcto: Evaluaciones de ámbito y tesitura completadas.")
        return True

    def _check_rhythm(self):
        """Regla de rítmica: Sólo redondas con margen de tolerancia para su correcta identificación."""

        # Margen de tolerancia del 5% para compensar exportaciones de DAWs como MuseScore o interpretaciones humanas si el usuario toca con metronomo.
        tolerance = self.whole_note_ticks * 0.05
        lower_bound = self.whole_note_ticks - tolerance
        upper_bound = self.whole_note_ticks + tolerance

        for i, duration in enumerate(self.note_durations):
            if not (lower_bound <= duration <= upper_bound):
                print(f"Error de figura rítmica en la nota {i+1}: Figura incorrecta, recuerda que en la primera especie se usan exclusivamente redondas.")
                return False

        print("Correcto: Toda la melodía está escrita en redondas.")
        return True

    def _check_climax(self):
        """Regla de clímax: Análisis del punto culminante."""
        climax_note = max(self.melody_notes)
        climax_count = self.melody_notes.count(climax_note)
        total_notes = len(self.melody_notes)
        climax_index = self.melody_notes.index(climax_note)

        # Climax unico: prohibicion de climax repetido
        if climax_count > 1:
            print(
                f"Error de clímax: La nota más alta ({climax_note}) se repite {climax_count} veces. El clímax debe ser único.")
            return False

        # Ubicacion del climax (No en extremos)
        if climax_index == 0 or climax_index == total_notes - 1:
            print("Error de clímax: El clímax no puede estar en el primer, ni en el último compás.")
            return False

        # Advertencia pedagogica: Preferentemente en el segundo tercio del ejercicio
        tercio_inicio = total_notes // 3
        tercio_fin = (total_notes * 2) // 3
        if not (tercio_inicio <= climax_index <= tercio_fin):
            print(
                f"Sugerencia de clímax: El clímax está en el compás {climax_index + 1}. Pedagógicamente se sugiere ubicarlo en el segundo tercio del ejercicio.")

        # Prohibicion de climax en la sensible (7mo grado)
        # Se calcula la sensible sumando 11 semitonos a la tonica
        sensible_pitch_class = (self.tonic_pitch_class + 11) % 12
        if (climax_note % 12) == sensible_pitch_class:
            print(
                f"Error de clímax: La nota clímax ({climax_note}) es la sensible ({self.tonic_name}). Esto genera una tensión acústica excesiva y poco estética.")
            return False

        print("Regla de clímax correcta: Único, bien ubicado y sin tensión de sensible.")
        return True

    def _check_repeated_notes(self) -> bool:
        """Regla de prohibición de notas repetidas consecutivas."""
        for i in range(len(self.melody_notes) - 1):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]

            if current_note == next_note:
                print(
                    f"Error: Nota repetida detectada ({current_note} y {next_note}). Está estrictamente prohibido repetir la misma nota consecutivamente en el Cantus Firmus.")
                return False

        print("Correcto: No hay notas repetidas consecutivamente.")
        return True

    def _check_stepwise_motion(self) -> bool:
        """Regla de predominio de grados conjuntos (Movimiento por segundas)."""
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
                f"Advertencia: Sólo el {stepwise_percentage:.1f}% de los movimientos son por grado conjunto. Se recomienda usar más movimientos de segunda para mayor fluidez vocal.")
        else:
            print(f"Correcto: Buen predominio de grados conjuntos ({stepwise_percentage:.1f}%).")

        # Siempre retorna true para no detener el analisis por cuestiones de estilo/estetica
        return True

    def _check_undulating_curve(self) -> bool:
        """Regla de contorno melódico: Curva ondulante estética con variedad direccional."""
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

            # Movimiento prolongado en la misma direccion (ERROR)
            if consecutive_direction == 5:
                print(
                    f"Error de conducción: Se detectó un perfil que se mueve en la misma dirección durante 6 notas.")
                return False

            # Falta de variedad direccional (ADVERTENCIA)
            elif consecutive_direction == 4:
                print(
                    f"Advertencia: Se detectó una serie de 5 notas en la misma dirección. Se recomienda alternar para mantener una curva más estética.")
                warning_triggered = True
                # No se retorna aqui para que el ciclo siga vigilando si llega a la 6ta nota

        # Si termino toda la pieza y nunca entro al warning
        if not warning_triggered:
            print("Regla de conducción correcta: La melodía tiene una curva ondulante con buena variedad direccional.")

        return True

    def _check_futile_oscillation(self) -> bool:
        """Regla de oscilación fútil: Advertencia para rebotes (tipo A-B-A)."""
        if len(self.melody_notes) < 3:
            return True

        for i in range(len(self.melody_notes) - 2):
            # Se compara la nota actual con la que esta dos posiciones adelante
            if self.melody_notes[i] == self.melody_notes[i + 2]:
                print(
                    f"Advertencia: Sugerencia: Oscilación detectada de ({self.melody_notes[i]} a {self.melody_notes[i + 1]} a {self.melody_notes[i + 2]}). Trata de evitar rebotes inmediatos para no estancar la fluidez de la línea.")
                return True

        print("Correcto: No hay oscilaciones fútiles (rebotes A-B-A).")
        return True

    def _check_sequences(self) -> bool:
        """Regla de secuencias: Evitar diseños rítmico-melódicos idénticos que se repitan a diferentes alturas."""
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

        print("Correcto: No se detectaron secuencias mecánicas similares.")
        return True

    def _check_valid_intervals(self) -> bool:
        """Reglas de intervalos: Saltos permitidos y prohibidos."""
        for i in range(len(self.melody_notes) - 1):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]
            interval_semitones = abs(current_note - next_note)

            # 1 = ascendente, -1 = descendente
            direction = 1 if next_note > current_note else -1

            # Salto mayor a una octava
            if interval_semitones > 12:
                print(
                    f"Error de salto: Salto mayor a una octava entre {current_note} y {next_note} ({interval_semitones} semitonos).")
                return False

            # Ignoramos los grados conjuntos (1 y 2 semitonos) porque no son saltos
            if interval_semitones in [1, 2]:
                continue

            # La 6ta menor (8 semitonos) solo se permite subiendo
            if interval_semitones == 8:
                if direction == -1:
                    print(
                        f"Error de salto: Sexta menor descendente detectada entre {current_note} y {next_note}. Este salto solo se permite en dirección ascendente.")
                    return False
                continue  # Si es ascendente, pasa

            # Saltos permitidos: 3m(3), 3M(4), 4J(5), 5J(7), 8J(12)
            allowed_leaps = [3, 4, 5, 7, 12]

            # Deteccion de intervalos prohibidos (Tritono, 6ta Mayor, septimas)
            if interval_semitones not in allowed_leaps:
                interval_names = {6: "Tritono (4ta Aum / 5ta dism)", 9: "Sexta Mayor", 10: "Séptima menor",
                                  11: "Séptima Mayor"}
                name = interval_names.get(interval_semitones, f"{interval_semitones} semitonos")

                # Se usa el traductor de notas para mostrar el nombre de las notas en lugar del numero MIDI
                nota1 = self._midi_to_name(current_note)
                nota2 = self._midi_to_name(next_note)

                print(f"Error de salto: Intervalo prohibido detectado ({name} entre {nota1} y {nota2}).")
                return False

        print("Regla de intervalos permitidos correcta: Todos los intervalos son válidos.")
        return True

    def _check_octave_leap(self) -> bool:
        """Regla de saltos de octava: Restricciones para la preparación y resolución del salto de octava dentro del ejercicio."""
        for i in range(len(self.melody_notes) - 1):
            current_note = self.melody_notes[i]
            next_note = self.melody_notes[i + 1]
            interval = abs(current_note - next_note)

            if interval == 12:
                # Usamos el traductor midi_to_name para las notas del salto
                nota1 = self._midi_to_name(current_note)
                nota2 = self._midi_to_name(next_note)

                # 1. Verificar que sea ascendente
                if next_note < current_note:
                    print(
                        f"Error de salto de 8va: Salto de octava descendente detectado ({nota1} a {nota2}). El salto de 8va solo es permitido si es ascendente.")
                    return False

                # 2. Verificar que sea precedida por grado conjunto descendente (si no es la primera nota)
                if i > 0:
                    prev_note = self.melody_notes[i - 1]
                    prev_interval = current_note - prev_note
                    # Debe ser descendente (negativo) y de grado conjunto (-1 o -2)
                    if prev_interval not in [-1, -2]:
                        nota_previa = self._midi_to_name(prev_note)
                        print(
                            f"Error de salto de 8va: El salto de octava ({nota1} a {nota2}) debe prepararse viniendo de un grado conjunto descendente (viene de un {nota_previa}).")
                        return False

                # 3. Verificar que sea seguida por grado conjunto descendente
                if i < len(self.melody_notes) - 2:
                    after_next_note = self.melody_notes[i + 2]
                    next_interval = after_next_note - next_note
                    # Debe ser descendente (negativo) y de grado conjunto (-1 o -2)
                    if next_interval not in [-1, -2]:
                        print(
                            f"Error de salto de 8va: El salto de octava ({nota1} a {nota2}) debe compensarse inmediatamente bajando por grado conjunto.")
                        return False
                else:
                    # Si entra aquí, significa que el salto de octava se intentó hacer en la última nota
                    print(
                        f"Error de salto de 8va: Salto de octava detectado al final del ejercicio ({nota1} a {nota2}). No hay espacio para compensarlo y rompe la cadencia final por grado conjunto.")
                    return False

        print("Regla de salto de octava correcta: Los saltos de octava (si los hay) cumplen la normativa de preparación y resolución.")
        return True

    def _check_leap_compensation(self) -> bool:
        """Regla de compensación de saltos: Tras saltos amplios, cambiar de dirección por grado conjunto."""
        # Saltos que exigen compensacion: 4J(5), 5J(7), 6m(8), 8J(12)
        leaps_to_compensate = [5, 7, 8, 12]

        for i in range(len(self.melody_notes) - 2):
            note1 = self.melody_notes[i]
            note2 = self.melody_notes[i + 1]
            note3 = self.melody_notes[i + 2]

            interval1 = abs(note1 - note2)

            # Si se encuentra un salto grande, se checa su resolución en la siguiente nota
            if interval1 in leaps_to_compensate:
                # Direcciones: 1 (Sube), -1 (Baja)
                dir1 = 1 if note2 > note1 else -1
                dir2 = 1 if note3 > note2 else -1

                interval2 = abs(note2 - note3)

                name1 = self._midi_to_name(note1)
                name2 = self._midi_to_name(note2)
                name3 = self._midi_to_name(note3)

                # 1. Verificar el cambio de direccion en movimiento contrario
                if dir1 == dir2:
                    direccion_texto = 'arriba' if dir2 == 1 else 'abajo'
                    print(
                        f"Error de compensación: El salto de ({name1} a {name2}) no fue compensado. La melodía debió cambiar de dirección por grado conjunto, pero continuó hacia {direccion_texto} a {name3}.")
                    return False

                # 2. Verificar que la compensacion sea por grado conjunto (1 o 2 semitonos)
                if interval2 not in [1, 2]:
                    print(
                        f"Error de compensación: El salto de ({name1} a {name2}) cambió de dirección, pero no por grado conjunto (saltó a un {name3}). Para la compensación se exige un movimiento de segunda.")
                    return False

        print(
            "Regla de compensación: Todos los saltos grandes fueron resueltos correctamente por grado conjunto en dirección contraria.")
        return True

    def _check_consecutive_leaps(self) -> bool:
        """Regla de saltos consecutivos: Prohibición de saltos consecutivos y manejo de terceras."""
        for i in range(len(self.melody_notes) - 2):
            note1 = self.melody_notes[i]
            note2 = self.melody_notes[i + 1]
            note3 = self.melody_notes[i + 2]

            int1 = abs(note2 - note1)
            int2 = abs(note3 - note2)

            dir1 = 1 if note2 > note1 else -1
            dir2 = 1 if note3 > note2 else -1

            # Si hay dos saltos en la misma dirección
            if dir1 == dir2:
                # Si ambos son saltos (mayores a una segunda / 2 semitonos)
                if int1 > 2 and int2 > 2:
                    name1 = self._midi_to_name(note1)
                    name2 = self._midi_to_name(note2)
                    name3 = self._midi_to_name(note3)

                    # Verificamos si son dos terceras consecutivas (3 o 4 semitonos)
                    if int1 in [3, 4] and int2 in [3, 4]:
                        total_interval = abs(note3 - note1)
                        if total_interval == 6:
                            print(
                                f"Error de tritono: Los saltos consecutivos de ({name1} a {name2} a {name3}) delinean un tritono.")
                            return False

                        # Deben cambiar de direccion en la siguiente nota
                        if i + 3 < len(self.melody_notes):
                            note4 = self.melody_notes[i + 3]
                            dir3 = 1 if note4 > note3 else -1
                            if dir3 == dir2:
                                name4 = self._midi_to_name(note4)
                                print(
                                    f"Error de compensación: Tras delinear los tonos ({name1}-{name2}-{name3}), la melodía no cambió de dirección, el perfil melódico siguió hacia {name4}.")
                                return False
                    else:
                        # Dos saltos amplios seguidos de diferente especie (ej. quinta y cuarta)
                        print(
                            f"Error de saltos: Dos saltos consecutivos en la misma dirección detectados ({name1} -> {name2} -> {name3}).")
                        return False

        print("Regla de saltos correcta: No hay exceso de saltos unidireccionales consecutivos.")
        return True

    def _check_outlined_tritone(self) -> bool:
        """Regla de tritono: Evitar delinear un tritono en los extremos de una curva melódica."""
        if len(self.melody_notes) < 3:
            return True

        start_idx = 0
        current_direction = 1 if self.melody_notes[1] > self.melody_notes[0] else -1

        for i in range(1, len(self.melody_notes) - 1):
            next_direction = 1 if self.melody_notes[i + 1] > self.melody_notes[i] else -1

            # si la linea cambia de direccion, revisamos el segmento que acaba de terminar
            if next_direction != current_direction:
                intervalo_extremos = abs(self.melody_notes[i] - self.melody_notes[start_idx])
                if intervalo_extremos == 6:
                    nota_ini = self._midi_to_name(self.melody_notes[start_idx])
                    nota_fin = self._midi_to_name(self.melody_notes[i])
                    print(
                        f"Error de tritono: La curva melódica delinea un tritono entre sus extremos ({nota_ini} y {nota_fin}).")
                    return False

                # Reiniciamos el inicio de la nueva curva
                start_idx = i
                current_direction = next_direction

        print("Regla de tritonos correcta: No se detectaron tritonos delineados (ocultos) en el ejercicio.")
        return True

    def _check_chromaticism(self) -> bool:
        """Regla de no cromatismos: Prohibición de alteraciones cromáticas."""
        # Estructura intervalica de la escala mayor (T, T, S, T, T, T, S)
        major_intervals = [0, 2, 4, 5, 7, 9, 11]
        valid_pitch_classes = [(self.tonic_pitch_class + i) % 12 for i in major_intervals]

        for note in self.melody_notes:
            if note % 12 not in valid_pitch_classes:
                nombre = self._midi_to_name(note)
                print(
                    f"Error de cromatismos: La nota {nombre} es un cromatismo no permitido en el modo mayor diatónico. En esta etapa solo se permiten notas diatónicas a {self.tonic_name} Mayor.")
                return False

        print(f"Regla de no cromatismos correcta: Todas las notas pertenecen a la escala de {self.tonic_name} Mayor.")
        return True

    def _check_cadence(self) -> bool:
        """Regla de cadencia final en los últimos 3 compases."""
        if len(self.melody_notes) < 3:
            return True

        antepenultimate = self.melody_notes[-3]
        penultimate = self.melody_notes[-2]
        ultimate = self.melody_notes[-1]

        # Grados relativos a la tonica
        supertonic_pc = (self.tonic_pitch_class + 2) % 12
        leading_tone_pc = (self.tonic_pitch_class + 11) % 12
        penultimate_pc = penultimate % 12

        # 1. El penultimo compas debe ser el 2do o 7mo grado
        if penultimate_pc not in [supertonic_pc, leading_tone_pc]:
            nota_pen = self._midi_to_name(penultimate)
            print(
                f"Error de cadencia final: El penúltimo compás tiene un {nota_pen}. Debe ser forzosamente la sensible (7mo grado) o la supertónica (2do grado).")
            return False

        # 2. Llegada exclusivamente por grado conjunto (maximo 2 semitonos de distancia)
        int_cadence_1 = abs(antepenultimate - penultimate)
        int_cadence_2 = abs(penultimate - ultimate)

        if int_cadence_1 > 2 or int_cadence_2 > 2:
            nota1 = self._midi_to_name(antepenultimate)
            nota2 = self._midi_to_name(penultimate)
            nota3 = self._midi_to_name(ultimate)
            print(
                f"Error de cadencia final: La llegada final de ({nota1} a {nota2} a {nota3}) tiene saltos superiores a 2 semitonos. Los últimos 3 compases deben resolverse exclusivamente por grado conjunto.")
            return False

        print("Regla de cadencia final correcta: El cierre cumple con las fórmulas 3-2-1 o 6-7-1 por grado conjunto.")
        return True

    def check_cantus_firmus_rules(self) -> bool:
        """Director de orquesta: Evalúa todas las reglas de forma secuencial."""
        if not self.melody_notes:
            print("No hay notas cargadas para evaluar.")
            return False

        print("\n--- Evaluando reglas de Cantus Firmus ---")

        if not self._check_valid_start_end(): return False
        if not self._check_structure_and_range(): return False
        if not self._check_rhythm(): return False
        if not self._check_climax(): return False
        if not self._check_repeated_notes(): return False
        if not self._check_stepwise_motion(): return False
        if not self._check_undulating_curve(): return False
        if not self._check_futile_oscillation(): return False
        if not self._check_sequences(): return False
        if not self._check_valid_intervals(): return False
        if not self._check_octave_leap(): return False
        if not self._check_leap_compensation(): return False
        if not self._check_consecutive_leaps(): return False
        if not self._check_outlined_tritone(): return False
        if not self._check_chromaticism(): return False
        if not self._check_cadence(): return False

        print("\nEl Cantus Firmus ha pasado todas las reglas estructurales y de movimiento.")
        return True


if __name__ == "__main__":
    engine = CounterpointEngine("cantus_test.mid", tonic_name="C")
    if engine.load_midi():
        engine.check_cantus_firmus_rules()