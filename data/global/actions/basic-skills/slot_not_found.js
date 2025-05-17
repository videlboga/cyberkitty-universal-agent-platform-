//CHECKSUM:3aeb5bc470939ae3dff875bd386dafff9c31b90f15e4899c28fd8065a84ba687
const hardLimit = 10

/**
 * Increment the "slot not found" counter.
 * When the counter reach its limit, the "notExtracted" flag is set and will make trigger the "On not found" transition.
 * @hidden true
 * @param retryAttempts The maximum number of times a slot extraction gets retried
 */
const slotNotFound = async retryAttempts => {
  if (!session.slots.notFound) {
    session.slots.notFound = 1
  }

  if (temp.tryFillSlotCount < Math.min(Number(retryAttempts), hardLimit)) {
    temp.tryFillSlotCount++
  } else {
    temp.notExtracted = 'true'
  }
}

return slotNotFound(args.retryAttempts)
