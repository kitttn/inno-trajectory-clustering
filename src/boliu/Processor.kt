package boliu

import java.io.*

/**
 * @author kitttn
 */

fun main(args: Array<String>) {
    val f = BufferedReader(FileReader(File("traj.txt")))
    val out = PrintWriter(File("traj_proc.txt"))
    var idx = 0
    val trajectory = mutableListOf<String>()

    for (line in f.lines()) {
        if (line.isNotEmpty())
            trajectory += line
        else {
            println("Saving trajectory #$idx")
            out.print("\n${idx++} ${trajectory.size / 2} ${trajectory.joinToString(" ")}")
            trajectory.clear()
        }
    }

    if (trajectory.isNotEmpty()) {
        println("Not empty, found smth more!")
        out.print("${idx} ${trajectory.size / 2} ${trajectory.joinToString(" ")}")
        trajectory.clear()
    }
}