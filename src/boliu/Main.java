package boliu;

public class Main {

    public static void main(String[] args) {
        TraClusterDoc tcd = new TraClusterDoc();
        tcd.onOpenDocument("traj_proc.txt");

        tcd.onClusterGenerate(args[1], 0.001, 4);

/**
 * To use the GUI, Remove the below comment and comment out the above section of code
 * An adjustable GUI is to be added.
 */
/*
        TraClusterDoc tcd = new TraClusterDoc();
		
		//tcd.onOpenDocument("src/deer_1995.tra");		
		//tcd.onClusterGenerate("testDeerResult.txt", 29, 8);
		
		//tcd.onOpenDocument("src/hurricane1950_2006.tra");
		//tcd.onClusterGenerate("testHurricaneResult.txt", 32, 6);
		
		tcd.onOpenDocument("src/elk_1993.tra");
		tcd.onClusterGenerate("testElkResult.txt", 25, 5);// 25, 5~7
		
		MainFrame mf = new MainFrame(tcd.m_trajectoryList, tcd.m_clusterList);
		
		
		Parameter p = tcd.onEstimateParameter();
		if (p != null) {
			System.out.println("Based on the algorithm, the suggested parameters are:\n" + "eps:" + p.epsParam + "  minLns:" + p.minLnsParam);
		}
*/
    }

}
