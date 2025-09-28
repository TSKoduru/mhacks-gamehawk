import { useState, useEffect, useCallback } from 'react';
import { motion } from 'motion/react';
import { WordHuntBoard } from './components/WordHuntBoard';
import { WordList, Word } from './components/WordList';
import { ControlPanel } from './components/ControlPanel';
import { Eye, Zap } from 'lucide-react';

// Sample 4x4 board
const sampleBoard = [
  ['C', 'A', 'T', 'S'],
  ['O', 'R', 'E', 'N'],
  ['W', 'D', 'O', 'G'],
  ['M', 'E', 'A', 'L']
];

// Sample words with coordinates [row, col]
const sampleWords: Word[] = [
  {
    word: 'CAT',
    coordinates: [[0, 0], [0, 1], [0, 2]], // C-A-T horizontal
    duration: 3,
    status: 'pending',
    definition: 'A small domesticated carnivorous mammal with soft fur, a short snout, and retractile claws.'
  },
  {
    word: 'DOG', 
    coordinates: [[2, 2], [2, 3], [2, 1]], // D-O-G (O back to D)
    duration: 4,
    status: 'pending',
    definition: 'A domesticated carnivorous mammal that typically has a long snout, an acute sense of smell, and a barking voice.'
  },
  {
    word: 'COW',
    coordinates: [[0, 0], [1, 0], [2, 0]], // C-O-W vertical
    duration: 3,
    status: 'pending',
    definition: 'A large domesticated ungulate animal with horns, hooves, and udders, kept for milk or meat.'
  },
  {
    word: 'READ',
    coordinates: [[1, 1], [1, 2], [2, 2], [2, 1]], // R-E-A-D
    duration: 5,
    status: 'pending',
    definition: 'To look at and comprehend the meaning of written or printed matter by mentally interpreting the characters or symbols.'
  },
  {
    word: 'MEAL',
    coordinates: [[3, 0], [3, 1], [3, 2], [3, 3]], // M-E-A-L horizontal
    duration: 4,
    status: 'pending',
    definition: 'An occasion when food is eaten, or the food that is eaten on such an occasion.'
  },
  {
    word: 'STAR',
    coordinates: [[0, 3], [0, 2], [0, 1], [1, 1]], // S-T-A-R
    duration: 5,
    status: 'pending',
    definition: 'A fixed luminous point in the night sky that is a large, remote incandescent body like the sun.'
  }
];

export default function App() {
  const [words, setWords] = useState<Word[]>(sampleWords);
  const [board, setBoard] = useState<string[][]>(sampleBoard);
  const [currentWordIndex, setCurrentWordIndex] = useState(-1);
  const [timeRemaining, setTimeRemaining] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const [isPaused, setIsPaused] = useState(false);
  const [highlightedTiles, setHighlightedTiles] = useState<number[][]>([]);

  const resetGame = useCallback(() => {
    setWords(sampleWords.map(word => ({ ...word, status: 'pending' })));
    setCurrentWordIndex(-1);
    setTimeRemaining(0);
    setIsPlaying(false);
    setIsPaused(false);
    setHighlightedTiles([]);
  }, []);

  const startNextWord = useCallback(() => {
    const nextPendingIndex = words.findIndex(word => word.status === 'pending');
    
    if (nextPendingIndex === -1) {
      // All words completed
      setIsPlaying(false);
      setCurrentWordIndex(-1);
      setHighlightedTiles([]);
      return;
    }

    setCurrentWordIndex(nextPendingIndex);
    setTimeRemaining(words[nextPendingIndex].duration);
    setHighlightedTiles(words[nextPendingIndex].coordinates);
    
    // Update word status to playing
    setWords(prev => prev.map((word, index) => 
      index === nextPendingIndex 
        ? { ...word, status: 'playing' }
        : word
    ));
  }, [words]);

  const completeCurrentWord = useCallback(() => {
    if (currentWordIndex >= 0) {
      setWords(prev => prev.map((word, index) => 
        index === currentWordIndex 
          ? { ...word, status: 'completed' }
          : word
      ));
      setHighlightedTiles([]);
      setCurrentWordIndex(-1);
      
      // Start next word after a brief pause
      setTimeout(() => {
        if (isPlaying && !isPaused) {
          startNextWord();
        }
      }, 1000);
    }
  }, [currentWordIndex, isPlaying, isPaused, startNextWord]);

  useEffect(() => {
    const ws = new WebSocket('ws://localhost:8765');

    ws.onopen = () => {
      console.log('Connected to WebSocket server');
    };

    ws.onmessage = (event) => {
      console.log('Received:', event.data);
      // set words
      try {
        const data = JSON.parse(event.data);
        setWords(data.words);
        setBoard(data.board);
      } catch (e) {
        console.error('Error parsing WebSocket message:', e);
      }
    };

    ws.onclose = () => {
      console.log('Disconnected from WebSocket server');
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
    };

    // Cleanup socket on unmount
    return () => {
      ws.close();
    };
  }, []);

  useEffect(() => {
    console.log("Words updated:", words);
    if (!isPlaying && words.length > 0) {
      console.log("Starting game");
      handlePlay();
    }
  }, [words]);


  // Timer effect
  useEffect(() => {
    if (!isPlaying || isPaused || currentWordIndex === -1) return;

    const timer = setInterval(() => {
      setTimeRemaining(prev => {
        if (prev <= 1) {
          completeCurrentWord();
          return 0;
        }
        return prev - 1;
      });
    }, 1000);

    return () => clearInterval(timer);
  }, [isPlaying, isPaused, currentWordIndex, completeCurrentWord]);

  const handlePlay = () => {
    if (isPaused) {
      setIsPaused(false);
    } else {
      setIsPlaying(true);
      startNextWord();
    }
  };

  const handlePause = () => {
    setIsPaused(true);
  };

  const completedWords = words.filter(word => word.status === 'completed').length;

  return (
    <div className="min-h-screen p-6" style={{ background: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)' }}>
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <motion.header 
          className="text-center mb-8"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          <img src="/logo.png" alt="GameHawk Logo" className="mx-auto mb-4 h-36" />
        </motion.header>

        {/* Main Content */}
        <div className="grid grid-cols-2 gap-8 items-start">
          {/* Game Board */}
          <motion.div 
            className="lg:col-span-1 flex justify-center"
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.2 }}
          >
            <WordHuntBoard 
              board={board}
              highlightedTiles={highlightedTiles}
              currentWord={currentWordIndex >= 0 ? words[currentWordIndex].word : undefined}
            />
          </motion.div>

          {/* Word List */}
          <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.3 }}
            className="lg:col-span-1 flex justify-center items-center h-full"
          >
            <WordList 
              words={words}
              currentWordIndex={currentWordIndex}
              timeRemaining={timeRemaining}
            />
          </motion.div>

          {/* Control Panel */}
          {/* <motion.div
            initial={{ opacity: 0, x: 20 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ delay: 0.4 }}
          >
            <ControlPanel
              isPlaying={isPlaying}
              isPaused={isPaused}
              onPlay={handlePlay}
              onPause={handlePause}
              onReset={resetGame}
              totalWords={words.length}
              completedWords={completedWords}
            />
          </motion.div> */}
        </div>
      </div>
    </div>
  );
}