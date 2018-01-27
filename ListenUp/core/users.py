from intbitset import intbitset

from typing import Any, Dict, Iterable, Tuple

from core.question_options import QuestionOptions
from core.questions import Question
from core.songs import Song
from util.annotations import override
from util.namedtuple_factory import register_namedtuple
from util.tupleable import Tupleable


@register_namedtuple
class User(Tupleable):
    """
    User POPO.
    
    :cvar DEFAULT_WINNING_POINTS default winning points needed to win a game
    :type DEFAULT_WINNING_POINTS int
    
    :ivar id DB id
    :type id int
    
    :ivar username username of the user
    :type username unicode
    
    :ivar points number of points the user has,
        i.e. the number of question the user completed
    :type points int
    
    :ivar questions set of question ids the user has already answered
    :type questions intbitset
    
    :ivar songs set of song ids the user has already answered
    :type songs intbitset
    
    The above fields are persisted in the DB.
    The below fields are per game and are only persisted in the HTTP session game.
    
    :ivar last_question_id the id of the last question attempted
    :type last_question_id int
    
    :ivar starting_points the number of points the user started the current game with
    :type starting_points int
    
    :ivar winning_points the number of points to win the current game
        defaults to `DEFAULT_WINNING_POINTS`
    :type winning_points int
    
    :ivar options trivia API options for new questions
    :type options Dict[str, Any]
    """
    
    DEFAULT_WINNING_POINTS = 5
    
    def __init__(self, id, username, points, questions, songs,
                 last_question_id=None, starting_points=None, winning_points=None, options=None):
        # type: (int, unicode, int, intbitset, intbitset, int, int, int, QuestionOptions) -> None
        self.id = id
        self.username = username
        self.points = points
        self.questions = questions
        self.songs = songs
        
        self.last_question_id = last_question_id
        
        if starting_points is None:
            starting_points = points
        self.starting_points = starting_points
        
        if winning_points is None:
            winning_points = User.DEFAULT_WINNING_POINTS
        self.winning_points = winning_points
        
        if options is None:
            options = QuestionOptions.default()
        self.options = options
    
    @classmethod
    def _make(cls, fields):
        # type: (Iterable[Any]) -> User
        return cls(*fields)
    
    @override
    def as_tuple(self):
        # type: () -> Tuple[int, unicode, int, intbitset, intbitset, int, int, int, QuestionOptions]
        return self.id, self.username, self.points, self.questions, self.songs, \
               self.last_question_id, self.starting_points, self.winning_points, self.options
    
    @staticmethod
    def _deserialize_intbitset(buf):
        # type: (buffer) -> intbitset
        ints = intbitset()
        ints.fastload(str(buf))
        return ints
    
    @staticmethod
    def _serialize_intbitset(ints):
        # type: (intbitset) -> buffer
        return buffer(ints.fastdump())
    
    @classmethod
    def from_db(cls, id, username, points, questions_buf, songs_buf):
        # type: (int, unicode, int, buffer) -> User
        return cls(id, username, points,
                   cls._deserialize_intbitset(questions_buf),
                   cls._deserialize_intbitset(songs_buf))
    
    def serialize_questions(self):
        # type: () -> buffer
        return self._serialize_intbitset(self.questions)
    
    def serialize_songs(self):
        # type: () -> buffer
        return self._serialize_intbitset(self.songs)
    
    def complete_question(self, question):
        # type: (Question) -> None
        """Complete `question` for self, incrementing points and questions."""
        self.points += 1
        self.questions.add(question.id)
    
    def play_song(self, song):
        # type: (Song) -> None
        """Record that `song` was played for self, adding to songs."""
        self.songs.add(song.id)
    
    def current_game_points(self):
        # type: () -> int
        """Get points in the current game."""
        return self.points - self.starting_points
    
    def has_won(self):
        # type: () -> bool
        """Check if user has won game yet."""
        won = self.current_game_points() >= self.winning_points
        if won:
            self.starting_points = self.points
        return won
    
    def set_options(self, options):
        # type: (Dict[str, str]) -> None
        """Set fields from dict where keys are `QuestionOptions`'s field names."""
        self.options.set_options(options)
