import os.path
import time
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import askopenfilenames
from tktooltip import ToolTip
from tinytag import TinyTag
import sqlite3
import pygame


global SONG_PLAYLIST
pygame.mixer.init()


def print_info():
    Label(text=get_flags('songsinplay'), background='salmon', foreground='white', width=3,
          font=('Times', '6')).place(x=375, y=161)


def set_back_song():
    CURSOR.execute("SELECT * FROM current")
    song = CURSOR.fetchall()
    if not song:
        return
    count_in_tree = get_flags('count')
    count_in_tree -= 1
    if count_in_tree == -1:
        count_in_tree = len(song) - 1
    if get_flags("addplay") == 1:
        tree.tag_configure('yellow', foreground="#BAF300")
        tree.item(get_flags("song_id"), tag='yellow')
        tree.set(get_flags("song_id"), 1, get_flags("end_duration"))
        tree.update()
        tree.selection_set(str(song[count_in_tree][7]))
    set_flags("song_id", song[count_in_tree][7])
    pygame.mixer.music.unload()
    set_flags('music_play', 0)
    play_music()


def next_song():
    CURSOR.execute("SELECT * FROM current")
    song = CURSOR.fetchall()
    if not song:
        return
    count_in_tree = get_flags('count')
    count_in_tree += 1
    if count_in_tree == len(song):
        count_in_tree = 0
    if get_flags("addplay") == 1:
        tree.tag_configure('yellow', foreground="#BAF300")
        tree.item(get_flags("song_id"), tag='yellow')
        tree.set(get_flags("song_id"), 1, get_flags("end_duration"))
        tree.update()
        tree.selection_set(str(song[count_in_tree][7]))
    set_flags("song_id", song[count_in_tree][7])
    pygame.mixer.music.unload()
    set_flags('music_play', 0)
    play_music()


def get_time(duration):
    duration /= 1000
    if duration < 0:
        return
    second = f"{0}{int(duration % 60)}"
    minute = '00' if (duration % 60) == 0 else f"{0}{int(duration / 60)}"
    hour = '00' if (duration % 3600) == 0 else f"{0}{int(duration / 3600)}"
    return f"{hour:}:{minute}:{second[0:] if len(second) < 3 else second[1:]}"


def move_end_duration(endduration):
    end_lbl = Label(frame_one, text=endduration, foreground="black", bg="LightSkyBlue3", font=('Algerian', '9'),
                    width=6)
    for position in range(400, 335, -1):
        time.sleep(0.005)
        end_lbl.place(x=position, y=132)
        end_lbl.update()


def new_song_play_settings(end, duration, songid):
    set_flags('duration', duration)
    set_flags("end_duration", end)
    set_flags("pause", 0)
    set_flags("song_id", songid)


def play_music():
    global progress, label_time, runlabel, POX, LENGHTSTRING
    if get_flags("music_play") == 1:
        play_time_duration()
        return
    CURSOR.execute("SELECT * FROM current")
    song = CURSOR.fetchall()
    if not song:
        return
    row = 0
    for count_song in range(0, len(song)):
        if song[count_song][7] == get_flags('song_id'):
            set_flags('count', count_song)
            row = count_song
            break
    long_name = song[row][0]
    name = song[row][5]
    end_duration = song[row][1]
    duration = song[row][6]
    new_song_play_settings(end_duration, duration, song[row][7])
    pygame.mixer.music.load(name)
    pygame.mixer.music.set_volume(volume_scale.get() / 100)
    pygame.mixer.music.play(loops=0)
    progress = ttk.Progressbar(frame_one, length=282, mode='determinate', value=0,
                               orient=HORIZONTAL, maximum=get_flags('duration') * 1000)
    progress.place(x=51, y=133)
    label_time = Label(frame_one, text="00:00:00", fg="black", bg="LightSkyBlue3", width=6, font=('Algerian', '9'))
    label_time.place(x=1, y=132)
    Label(frame_one, text=long_name, bg="LightSkyBlue1", font=('Impact', '11'), width=54).place(x=1, y=5)

    # print("Title:", song.title)
    # print("Artist:",  song.artist)
    # print("Genre:", song.genre)
    # print("Year Released:", song.year)
    # print("Bitrate:", song.bitrate, "kBits/s")
    # print("Composer:", song.composer)
    # print("Filesize:", song.filesize, "bytes")
    # print("AlbumArtist:", song.albumartist)
    # print("Duration:", song.duration, "seconds")
    # print("TrackTotal:",  song.track_total)

    set_flags("first_", 1)
    set_flags('music_play', 1)
    move_end_duration(end_duration)
    play_time_duration()



def continue_play_music():
    set_flags('pause', 0)
    pygame.mixer.music.unpause()
    play_time_duration()


def play_time_duration():
    while get_time(pygame.mixer.music.get_pos()) != get_flags('end_duration'):
        pygame.mixer.music.set_volume(volume_scale.get() / 100)
        if get_flags("addplay") == 1:
            tree.tag_configure('green2', foreground='green2')
            tree.item(get_flags("song_id"), tag='green2')
            tree.set(get_flags("song_id"), 1, get_time(pygame.mixer.music.get_pos()))
        progress.config(value=pygame.mixer.music.get_pos())
        progress.update()
        label_time.config(text=get_time(pygame.mixer.music.get_pos()), fg="black")
        label_time.update()
    set_flags('music_play', 0)
    next_song()


def pause_music():
    if get_flags('first_') == 0:
        return
    if get_flags('pause') == 0:
        pygame.mixer.music.pause()
        set_flags('pause', 1)
    else:
        set_flags('pause', 0)
        continue_play_music()


def add_song_in_playlist(playlistbox):
    allowed_extensions = ('.mp3', '.wav', ".mp4", '.avi')
    song_files = []
    songs = list(askopenfilenames())
    for element in songs:
        for ext in allowed_extensions:
            if element.find(ext) != -1:
                song_files += (element,)
                break
    if song_files == "":
        return
    for song_file in song_files:
        song = TinyTag.get(song_file)
        song.artist = song.artist.replace('[', "(").replace("]", ")")
        text_name = f"{song.title} -> {song.artist}"
        text_time = f"{get_time(song.duration * 1000)}"
        sqlite_insert_with_param = """INSERT INTO current (songname, duration, artist, bitrate, playlist, path,
                duration_second) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        new_client = [text_name, text_time, song.artist, int(song.bitrate), get_flags('playlist'), song_file,
                      song.duration]
        CURSOR.execute(sqlite_insert_with_param, new_client)
    BASE_BD.commit()

    update_playlist(playlistbox)

    # song = TinyTag.get(song_file)
    # song = TinyTag.get(song_file)
    # print("Title:", song.title)
    # print("Artist:",  song.artist)
    # print("Genre:", song.genre)
    # print("Year Released:", song.year)
    # print("Bitrate:", song.bitrate, "kBits/s")
    # print("Composer:", song.composer)
    # print("Filesize:", song.filesize, "bytes")
    # print("AlbumArtist:", song.albumartist)
    # print("Duration:", song.duration, "seconds")
    # print("TrackTotal:",  song.track_total)


def update_playlist(playlisttree):
    SONG_PLAYLIST = []
    for row in list(CURSOR.execute("SELECT * FROM current")):
        SONG_PLAYLIST.append([row[0], row[1], row[7], row[5]])
    if SONG_PLAYLIST == []:
        return
    else:
        set_flags('count', 0)
    for delete_row in playlisttree.get_children():
        playlisttree.delete(delete_row)
    songs = []
    set_flags("songsinplay", len(SONG_PLAYLIST))
    print_info()
    for element in SONG_PLAYLIST:
        songs.append(list(element))
    for element in songs:
        if os.path.exists(element[3]):
            playlisttree.insert("", END, iid=str(element[2]), values=element)



def get_flags(name_flag):
    CURSOR.execute(f"SELECT {name_flag} FROM flags")
    trigger = CURSOR.fetchone()[0]
    return trigger


def set_flags(name_flag, trigger):
    if isinstance(trigger, int):
        CURSOR.execute(f"UPDATE flags SET {name_flag} = {trigger}")
    else:
        CURSOR.execute(f"UPDATE flags SET {name_flag} = '{trigger}'")
    BASE_BD.commit()


def save_playlist(pattern, label):
    flag = get_flags('flag_entry')
    if flag == 1:
        return
    file_name = Entry(pattern, width=30, font="Ariel 8")
    file_name.place(x=90, y=370)
    file_name.insert(0, get_flags('playlist'))
    save_button = Button(pattern, text="ОК", width=3,
                         command=lambda: press_ok_save(pattern, file_name, save_button, label))
    save_button.place(x=277, y=368)
    file_name.focus_set()


def press_ok_save(win, filename, savebtn, labelplaylist):
    name = filename.get()
    set_flags(name_flag='playlist', trigger=name)
    set_flags('flag_entry', 0)
    if name == "":
        return
    CURSOR.execute(f"UPDATE current SET playlist = '{get_flags('playlist')}'")
    CURSOR.execute(f"SELECT * FROM plists WHERE playlist = '{get_flags('playlist')}'")
    rows_db = CURSOR.fetchone()
    if rows_db is not None:
        CURSOR.execute(f"DELETE FROM plists WHERE playlist = '{get_flags('playlist')}'")
    rows_save = []
    for row_db in CURSOR.execute("SELECT * FROM current"):
        rows_save.append(row_db)
    for element in rows_save:
        sqlite_insert_with_param = """INSERT INTO plists (songname, duration, artist, bitrate, playlist, path,
                        duration_second) VALUES (?, ?, ?, ?, ?, ?, ?)"""
        CURSOR.execute(sqlite_insert_with_param, element[0:7])
    BASE_BD.commit()
    savebtn.destroy()
    filename.destroy()
    change_color_labeb(labelplaylist)


def change_color_labeb(label):
    for color in range(255, 20, -1):
        time.sleep(0.001)
        label.config(foreground=f"#{color:X}{color:X}{color:X}")
        label.update()
    text = f"Название: {get_flags('playlist')}" \
        if len(f"Название: {get_flags('playlist')}") < 55 else f"Название: {get_flags('playlist')[0:52]}..."
    label.config(text=text)
    label.update()
    for color in range(20, 255):
        time.sleep(0.001)
        label.config(foreground=f"#{color:X}{color:X}{color:X}")
        label.update()
    label.config(foreground='yellow')
    label.update()
    ToolTip(label, msg=f"{get_flags('playlist')}", follow=False)


def open_playlist(parent, tree_table, label):
    CURSOR.execute("SELECT playlist FROM plists GROUP BY playlist")
    rows = CURSOR.fetchall()
    if rows is None:
        return
    win_playlists = Toplevel(parent)
    position = parent.geometry()
    dx = position[position.index('+') + 1:][0:position[position.index('+') + 1:].index("+")]
    dy = position[position.index('+') + 1:][position[position.index('+') + 1:].index("+") + 1:]
    shift = int(dy)
    if (805 + int(dx)) > root.winfo_screenwidth():
        dx = str(int(dx) - 1205)
    if shift < 0:
        shift = int(dy)
    win_playlists.geometry(f"310x400+{400 + int(dx)}+{shift}")
    win_playlists.config(background='black')
    win_playlists.title("ВЫБОР СПИСКА ВОСПРОИЗВЕДЕНИЯ")
    Label(win_playlists, text="Выделите нужные списки CTRL и SHIFT", width=44,
          background='green', foreground='yellow', relief='groove').place(y=0, x=0)
    select_listbox = Listbox(win_playlists, width=51, height=21, background='black', selectmode=EXTENDED)
    select_listbox.place(x=0, y=20)

    addselectedpng = PhotoImage(file="IMG/add_selected.png")
    addselected_button = Button(win_playlists, image=addselectedpng, background='black', borderwidth=0,
                                activebackground='black',
                                command=lambda: add_selected_playlist(win_playlists, select_listbox, tree_table))
    addselected_button.place(x=5, y=363)
    ToolTip(addselected_button, msg='Добавить выбранные списки в список воспроизведения', follow=False)

    deleteselectedpng = PhotoImage(file="IMG/delete_selected.png")
    deleteselected_button = Button(win_playlists, image=deleteselectedpng, background='black', borderwidth=0,
                                   activebackground='black')
    deleteselected_button.place(x=42, y=363)
    ToolTip(deleteselected_button, msg='Удалить выбранные списки', follow=False)
    show_playlist(win_playlists, select_listbox, rows)
    if get_flags("first_") == 1:
        play_music()
    win_playlists.wait_window()


def show_playlist(win, selectlistbox, songs):
    selectlistbox.delete(0, END)
    for element in songs:
        selectlistbox.insert(END, element)
    selectlistbox.select_set(0, 0)
    selectlistbox.focus_set()
    for color in range(20, 255):
        time.sleep(0.001)
        selectlistbox.config(foreground=f"#{color:X}{color:X}{color:X}")
        selectlistbox.update()
    selectlistbox.update()


def add_selected_playlist(win, selectlistbox, treetable):
    adds_element = []
    elements = selectlistbox.selection_get().replace("\n", ", ").replace("{", "").replace("}", "").split(", ")
    for element in elements:
        adds_element.append(element)
    win.destroy()
    for playlist in adds_element:
        CURSOR.execute(f"SELECT * FROM plists WHERE playlist = '{playlist}'")
        songs = CURSOR.fetchall()
        for element in songs:
            sqlite_insert_with_param = """INSERT INTO current (songname, duration, artist, bitrate,
            playlist, path, duration_second) VALUES (?, ?, ?, ?, ?, ?, ?)"""
            CURSOR.execute(sqlite_insert_with_param, element)
    BASE_BD.commit()
    update_playlist(treetable)


def delete_selected(treelist):
    for element in treelist.selection():
        print(treelist.index(element))


def add_playlist(parrent):
    global win_add, tree
    set_flags("addplay", 1)
    addplayist_button.config(state=DISABLED)
    win_add = Toplevel(parrent)
    win_add.config(background='black')
    win_add.title("СПИСКОК ВОСПРОИЗВЕДЕНИЯ")
    win_add.protocol("WM_DELETE_WINDOW", lambda: (addplayist_button.config(state=ACTIVE, activebackground="black"),
                                                  set_flags("addplay", 0), win_add.destroy()))
    position = parrent.geometry()
    dx = position[position.index('+') + 1:][0:position[position.index('+') + 1:].index("+")]
    dy = position[position.index('+') + 1:][position[position.index('+') + 1:].index("+") + 1:]
    shift = int(dy) - 200
    if (805 + int(dx)) > root.winfo_screenwidth():
        dx = str(int(dx) - 805)
    if shift < 0:
        shift = int(dy)
    win_add.geometry(f"394x400+{405 + int(dx)}+{shift}")
    text = f"Название: {get_flags('playlist')}" \
        if len(f"Название: {get_flags('playlist')}") < 55 else f"Название: " \
                                                               f"{get_flags('playlist')[0:52]}..."
    label_playlist = Label(win_add, text=f"{text}", background='black', foreground='white')
    label_playlist.config(font="Courier 9 bold", foreground='yellow')
    label_playlist.pack(anchor=N)
    ToolTip(label_playlist, msg=f"{get_flags('playlist')}", follow=False)

    frame_two = Frame(win_add, height=332, width=392)
    frame_two.place(x=1, y=25)

    columns = ("name_song", "time_song")
    tree = ttk.Treeview(frame_two, name="tree",  columns=columns, show="headings", height=15, padding=5)
    ttk.Style().configure("Treeview", background="black", foreground="#BAF300", fieldbackground="black")
    tree.pack(side=LEFT)
    tree.heading("name_song", text="Наименование", anchor=W)
    tree.heading("time_song", text="Время", anchor=W)
    tree.column("#1", stretch=NO, width=310, anchor=W)
    tree.column("#2", stretch=NO, width=50, anchor=E)
    tree.bind("<Return>", keypress_tree_change_song)
    tree.bind("<KP_Enter>", keypress_tree_change_song)
    tree.bind("<KP_Enter>", keypress_tree_change_song)
    tree.bind("<Double-ButtonPress-1>", keypress_tree_change_song)
    scrollbar = Scrollbar(frame_two, orient=VERTICAL, command=tree.yview)
    tree["yscrollcommand"] = scrollbar.set
    scrollbar.place(y=0, x=374)
    scrollbar.pack(side="right", fill="y")

    update_playlist(tree)

    addsonginplaylistpng = PhotoImage(file="IMG/add_songs.png")
    addpsonginlayist_button = Button(win_add, image=addsonginplaylistpng, borderwidth=0, background='black',
                                     activebackground='black', command=lambda: add_song_in_playlist(tree))
    addpsonginlayist_button.place(x=5, y=363)
    ToolTip(addpsonginlayist_button, msg='Добавить песни из файлов на ваших дисках', follow=False)

    deleteselectpng = PhotoImage(file="IMG/delete.png")
    deleteselect_button = Button(win_add, image=deleteselectpng, background='black', borderwidth=0,
                                 activebackground='black', command=lambda: delete_selected(tree))
    deleteselect_button.place(x=40, y=363)
    ToolTip(deleteselect_button, msg='Удалить из списка выбранные песни', follow=False)
    addplaylistpng = PhotoImage(file="IMG/add_fromfile.png")
    addplaylist_button = Button(win_add, image=addplaylistpng, background='black', borderwidth=0,
                                activebackground='black', command=lambda: open_playlist(win_add, tree, label_playlist))
    addplaylist_button.place(x=323, y=363)
    ToolTip(addplaylist_button, msg='Добавить другой список или из другого списка', follow=False)
    saveplaylistpng = PhotoImage(file="IMG/save_playlist.png")
    saveplaylist_button = Button(win_add, image=saveplaylistpng, background='black', borderwidth=0,
                                 activebackground='black', command=lambda: save_playlist(win_add, label_playlist))
    saveplaylist_button.place(x=358, y=363)
    ToolTip(saveplaylist_button, msg='Сохранить список воспроизведения', follow=False)

    CURSOR.execute(f"SELECT * FROM current WHERE id = {get_flags('song_id')}")
    row = CURSOR.fetchone()
    if row is not None:
        set_flags('song_id', row[7])
        tree.selection_set(str(get_flags('song_id')))
    win_add.resizable(False, False)
    if get_flags("first_") == 1:
        play_music()
    tree.focus_set()
    win_add.wait_window()


def keypress_tree_change_song(event):
    if tree.selection() == ():
        return
    tree.tag_configure('yellow', foreground="#BAF300")
    tree.item(get_flags("song_id"), tag='yellow')
    tree.set(get_flags("song_id"), 1, get_flags("end_duration"))
    tree.update()
    pos = int(tree.selection()[0])
    CURSOR.execute(f"SELECT * FROM current WHERE id = {pos}")
    row = CURSOR.fetchone()
    set_flags('song_id', row[7])
    set_flags('music_play', 0)
    play_music()


def setvolume(volumescale):
    print(volume_scale.get() / 100)


def exit_programm():
    root.destroy()


if __name__ == "__main__":
    global root, volume_scale, frame_one, addplayist_button
    POX = 0
    LENGHTSTRING = 0
    SONG_PLAYLIST = []
    BASE_BD = sqlite3.connect('playlist.db')
    CURSOR = BASE_BD.cursor()
    set_flags('flag_entry', 0)
    set_flags('pause', 0)
    set_flags('music_play', 0)
    set_flags('first_', 0)
    set_flags('quit', 0)
    set_flags("addplay", 0)
    CURSOR.execute("SELECT * FROM current")
    rows = CURSOR.fetchall()
    set_flags("songsinplay", len(rows))
    if len(rows) != 0:
        set_flags('playlist', rows[0][4])
        set_flags('song_id', rows[0][7])
        set_flags('count', 0)
        for count in range(len(rows)):
            SONG_PLAYLIST.append([rows[count][0], rows[count][1], rows[count][7]])
    else:
        set_flags('end_duration', "00:00:00")
        set_flags('count', 0)
        set_flags('playlist', "*без названия*")
        set_flags('song_id', 0)
        set_flags('duration', 0)
    root = Tk()
    ttk.Style().theme_use('winnative')
    root.title("Лирик MP3 проигрыватель")
    root.iconbitmap(default="IMG/icon2.ico")
    root.geometry(f"400x200+0+{root.winfo_screenheight() - 300}")
    root.resizable(False, False)
    root.config(background="black")
    root.protocol("WM_DELETE_WINDOW", exit_programm)

    ttk.Label(text="volume", background="black", foreground="green").place(y=170, x=195-43)
    volume_scale = Scale(root, bg="black", foreground='yellow', orient=HORIZONTAL, font=('Algerian', '8'),
                         width=10, from_=1, to=100, showvalue=False, activebackground="black")
    volume_scale.place(x=200, y=172)
    volume_scale.set(value=50)
    frame_one = Frame(name="main", width=390, height=153, borderwidth=2, relief=GROOVE, bg="LightSkyBlue3", bd=2,)
    frame_one.place(x=5, y=5)

    stoppng = PhotoImage(file="IMG/pause.png")
    stop_button = Button(root, image=stoppng, borderwidth=0, background="black", activebackground="black",
                         command=pause_music)
    stop_button.place(x=5, y=163)
    ToolTip(stop_button, msg='Пауза', follow=False)

    playpng = PhotoImage(file="IMG/play.png")
    play_button = Button(root, image=playpng, borderwidth=0, background="black", activebackground="black",
                         command=play_music)
    play_button.place(x=42, y=163)
    ToolTip(play_button, msg='Воспроизведение', follow=False)

    previouspng = PhotoImage(file="IMG/previous.png")
    previous_button = Button(root, image=previouspng, borderwidth=0, background="black", activebackground="black",
                             command=set_back_song)
    previous_button.place(x=79, y=163)
    ToolTip(previous_button, msg='Предыдущий трек', follow=False)

    nextpng = PhotoImage(file="IMG/next.png")
    next_button = Button(root, image=nextpng, borderwidth=0, background="black", activebackground="black",
                         command=next_song)
    next_button.place(x=116, y=163)
    ToolTip(next_button, msg=f"Следующий трек", follow=False)

    settingspng = PhotoImage(file="IMG/settings.png")
    settings_button = Button(root, image=settingspng, borderwidth=0, background="black", activebackground="black")
    settings_button.place(x=363 - 45, y=163)
    ToolTip(settings_button, msg='Настройки', follow=False)
    addplaylistpng = PhotoImage(file="IMG/add_playlist.png")
    addplayist_button = Button(root, image=addplaylistpng, borderwidth=0, background="black", activebackground="black",
                               command=lambda: add_playlist(root))
    addplayist_button.place(x=355, y=163)
    ToolTip(addplayist_button, msg='Список воспроизведения', follow=False)
    print_info()
    root.resizable(False, False)
    root.focus_force()
    # add_playlist(root)
    root.mainloop()
