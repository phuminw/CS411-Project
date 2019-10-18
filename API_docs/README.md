# APIs

### Youtube Query
- Required parameters
    - q(String): query string
    - n(int): number of result(s), must be non-negative
- Optional parameter
    - thumb_size(String): size of desire thumbnail high, medium, default (default behavior is no thumbnail returned)

#### Example call
`query('Trump', 2)`
`query('Taylor Swift', 3, 'high')`

### Spotify