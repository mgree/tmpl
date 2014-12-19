module Sessions where

import System.Environment
import System.Exit

import Data.Char
import qualified Data.Map as Map
import qualified Data.Set as Set

main :: IO ()
main = do   
  input <- parseArgs
  f <- readFile input
  let ls = lines f
  let ys = parse ls
  putStrLn $ "Found " ++ show (length ys) ++ " years."

newtype Author = Author { authorName :: String }
data Paper = Paper { title :: String, authors :: [Author] }
newtype Session = Session { papers :: [Paper] }
data Year = Year { year :: String, sessions :: [Session] }

parse :: [String] -> [Year]
parse ls = 
  let ys = breakUp "* " ls in
  map (\(y,ss) -> Year y (sessions ss)) ys
  where sessions ss = map (\(_,ps) -> Session $ papers ps) $ breakUp "** " ss
        papers ps = map (\(p,as) -> Paper p (map Author as)) $ breakUp "*** " ps

breakUp :: String -> [String] -> [(String,[String])]
breakUp _ [] = []
breakUp bk (l:ls) = 
  if breakable l
  then let (lcts,rest) = break breakable ls in 
  (l,filter (not . all isSpace) lcts) : breakUp bk rest  
  else breakUp bk ls
  where breakable line = take (length bk) line == bk
        
          
parseArgs :: IO String
parseArgs = do
  args <- getArgs
  case args of
    [filename] -> return filename
    _ -> do
      name <- getProgName
      putStrLn $ "Usage: " ++ name ++ " filename"
      exitFailure