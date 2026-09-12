-- dual_consume.lua
-- validate-all-then-write-all; same-slot keys; {ok}|{err}
-- KEYS: slot keys to consume (typically one: dual:<action_hash>)
-- ARGV: request_id, action_hash, seat_a, seat_b, consumed_at
--
-- If ANY key already exists, write nothing and return {err}.
-- If ALL keys are free, HSET every key with the same ARGV and return {ok}.

for i = 1, #KEYS do
  if redis.call("EXISTS", KEYS[i]) == 1 then
    return "{err}"
  end
end

for i = 1, #KEYS do
  redis.call(
    "HSET", KEYS[i],
    "request_id", ARGV[1],
    "action_hash", ARGV[2],
    "seat_a", ARGV[3],
    "seat_b", ARGV[4],
    "consumed_at", ARGV[5]
  )
end

return "{ok}"
